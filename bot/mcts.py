"""# ``mcts` Module
Module implementing Monte Carlo Tree Search algorithm to search for the\
    most promising move from a Tic-Tac-Toe/Ultimate Tic-Tac-Toe game state.
"""
import math
import random as rand

from bot.gamestate import (
    GameState,
    UltimateGameState,
    get_winner
)

from typing import (
    Iterator,
    Optional,
    Literal
)
from bot.gamestate import PlayerCharacter

import logging
logger = logging.getLogger()


class MonteCarloNode:
    """
    Class representing the nodes of a Monte Carlo Search Tree.\
        This class is supposed to extend the GameState classes in `gamestate` modules\
        for purpose of the Monte Carlo Tree Search algorithm.

    ## Attributes (read-only):
    `children` (`Iterator[MonteCarloNode]`): the children of the current node.
    `parent` (`MonteCarloNode`): the parent node of the current node.
    `fully_expanded` (`bool`): returns whether or not the current node is fully expanded.
    `is_terminal` (`bool`): returns whether or not the current node is a terminal node.
    `uct` (`float`): the uct score of the current node.
    `visits` (`int`): the number of times the node has been visited.
    `winner` (`Optional[Literal['X', 'O', 'T']]`): the winner of the game state at the current node.
    `wins` (`float`): the number of times the node reaches a winning state.

    ## Methods:
    `playouts()`
    `update()`
    """
    __slots__ = '_state', '_visits', '_wins',\
                '_c_coef', '_c_rave', '_amaf_wins', '_amaf_sims',\
                '_children', '_parent',
    def __init__(self, state: GameState | UltimateGameState,
                 c_coefficient: float = math.sqrt(2),
                 **kwargs):
        """
        Initialize Monte Carlo node.

        ## Parameters:
        `state`: `GameState` or `UltimateGameState` representing the current state.
        `c_coefficient`: a float representing the c coefficient in the [UCT formula](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search#Exploration_and_exploitation).
        """
        self._state: GameState = state
        self._visits: int = 0
        self._wins: float = 0
        self._children: list[MonteCarloNode] = []
        self._parent: Optional[MonteCarloNode] = kwargs['parent'] if 'parent' in kwargs else None
        self._c_coef = c_coefficient
        self._c_rave = 20
        self._amaf_sims = 0
        self._amaf_wins = 0

    @property
    def uct(self) -> float:
        """
        The UCT score of a Monte Carlo node.\
            See [here](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search#Exploration_and_exploitation)\
            for more information.
        """
        # num win / num visits + c * sqrt(ln(parent visits) / num visits)
        if self._parent is None:
            raise AttributeError('Node has no parent')
        if not self._visits: return math.inf

        return self._wins / self._visits +\
               self._c_coef * math.sqrt(math.log(self._parent.visits) / self._visits)
    @property
    def rave(self) -> float:
        alpha = max(0, (self._c_rave - self._visits) / self._c_rave)
        amaf = self._amaf_sims / (self._amaf_sims + self._visits + 4 * self._amaf_sims * self._visits)
        return alpha * amaf + (1 - alpha) * self.uct
    @property
    def visits(self) -> int:
        """The number of times the current node has been visited"""
        return self._visits
    @property
    def wins(self) -> float:
        """
        The number of winning states the current node has reached through simulation.\
            For situations that ended in a tie, `wins` is incremented by 0.5.
        """
        return self._wins
    
    @property
    def winner(self) -> Optional[PlayerCharacter | Literal['T']]:
        """
        The winner at the current game state. If the current game state is\
            not terminal, i.e, the game is not over then None is returned.
        """
        return self._state.game_over
    @property
    def is_terminal(self) -> bool:
        """A node is terminal if it results in a win/loss/tie"""
        return (not self._state.game_over is None)
    @property
    def fully_expanded(self) -> bool:
        """A node is fully_expanded if it has children and every children has been visited"""
        return len(self._children) and all(child.visits for child in self._children)
    
    @property
    def parent(self) -> 'MonteCarloNode':
        """The parent node of the current node, root node has no parent."""
        return self._parent
    @property
    def children(self) -> Iterator['MonteCarloNode']:
        """
        The children nodes of the current node, terminal nodes do not have any children.
        Note: An Iterator is returned for the property. 
        """
        if not len(self._children): self._expand()
        return iter(self._children)
    

    def _expand(self) -> None:
        for new_state in self._state.expand_state():
            self._children.append(MonteCarloNode(new_state, self._c_coef, parent=self))

    def playouts(self) -> list[GameState | UltimateGameState]:
        """
        Return all of the possible moves from a position.
        
        ## Return
        A list of GameStates and UltimateGameState.
        """
        return self._state.expand_state()

    def update(self, result: PlayerCharacter | Literal['T']):
        """
        Update the current node from a simulation's result
        
        ## Parameters:
        `result`: a string literal of `'X'`, `'O'` or `T`
        """
        self._visits += 1
        if result == 'T': self._wins += .5
        elif self._state.play_char != result: self._wins += 1
        else: self._wins -= 1

    def update_amaf(self, result: PlayerCharacter | Literal['T']):
        """
        Update the current node from a simulation's result
        
        ## Parameters:
        `result`: a string literal of `'X'`, `'O'` or `T`
        """
        self._amaf_sims += 1
        if result == 'T': self._amaf_wins += .5
        elif self._state.play_char != result: self._amaf_wins += 1

def monte_carlo_search(root: MonteCarloNode, max_iter: int = 1000, *,
                       kill_signal: list[bool])\
    -> MonteCarloNode:
    """
    Monte Carlo Tree Search on Tic-Tac-Toe
    
    ## Parameters:
    `root`: the root node
    `max_iter`: maximum iteration to run for
    `kill_signal`: external stopping condition. This should be a list of ONE `bool` value,\
        a list is not necessary, any mutable container can be used.

    ## Return
    The root node after searching, to get the best move, take the child with the most visits.
    """
    if root.is_terminal: return

    i = -1
    while ((i := i + 1) < max_iter) and (not kill_signal[0]):
        leaf_node = _traversal(root, kill_signal)

        # the game has ended
        if leaf_node is None: continue
        simulation_result = _simulation(leaf_node, kill_signal)

        _backpropogate(leaf_node, *simulation_result, kill_signal)
    return root

def _traversal(node: MonteCarloNode, kill_signal: list[bool])\
    -> MonteCarloNode:
    """Selection and expansion state in Monte Carlo Tree Search"""
    # selection
    while node.fully_expanded and (not kill_signal[0]):
        node = max(node.children, key=lambda child: child.rave)

    # expansion
    for child in node.children:
        if kill_signal[0]: return
        if not child.visits: return child

def _simulation(node: MonteCarloNode, kill_signal: list[bool])\
    -> PlayerCharacter | Literal['T']:
    """Simulation state in Monte Carlo Tree Search. Playout is selected randomly"""
    amaf_history = set()
    while not node.is_terminal and (not kill_signal[0]):
        node = rand.choice(list(node.children))
        amaf_history.update(node._state.previous_move)

    return ('T' if (winner := get_winner(node._state._board_state)) is None else winner), amaf_history

def _backpropogate(node: MonteCarloNode, result: PlayerCharacter | Literal['T'],
                   amaf_history: set[tuple], kill_signal: list[bool]):
    play_char = node._state.play_char
    while node and (not kill_signal[0]):
        if node.parent:
            for sibling in node.parent.children:
                if (play_char == sibling._state.play_char) and\
                   (sibling._state.previous_move in amaf_history):
                    sibling.update_amaf(result)
        node.update(result)
        node = node.parent