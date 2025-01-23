import math
import random as rand

from bot.gamestate import GameState, UltimateGameState, get_winner

from typing import Iterator, Optional, Literal
from bot.gamestate import PlayerCharacter

class MonteCarloNode:
    __slots__ = '_state', '_visits', '_wins',\
                '_c_coef',\
                '_children', '_parent'
    def __init__(self, state: GameState | UltimateGameState, c_coefficient: float = math.sqrt(2), **kwargs):
        self._state: GameState = state
        self._visits: int = 0
        self._wins: float = 0
        self._children: list[MonteCarloNode] = []
        self._parent: Optional[MonteCarloNode] = kwargs['parent'] if 'parent' in kwargs else None
        self._c_coef = c_coefficient

    @property
    def uct(self) -> float:
        # num win / num visits + c * sqrt(ln(parent visits) / num visits)
        if self._parent is None:
            raise AttributeError('Node has no parent')
        if not self._visits: return math.inf

        return self._wins / self._visits +\
               self._c_coef * math.sqrt(math.log(self._parent.visits) / self._visits)
    @property
    def visits(self) -> int:
        return self._visits
    @property
    def wins(self) -> float:
        return self._wins
    
    @property
    def winner(self) -> Optional[PlayerCharacter | Literal['T']]:
        winner = get_winner(self._state._board_state)
        return 'T' if (winner is None) and self.is_terminal else winner
    @property
    def is_terminal(self) -> bool:
        """A node is terminal if it results in a win/loss/tie"""
        return self._state.game_over
    @property
    def fully_expanded(self) -> bool:
        """A node is fully_expanded if it has children and every children has been visited"""
        return len(self._children) and all(child.visits for child in self._children)
    
    @property
    def parent(self) -> 'MonteCarloNode':
        return self._parent
    @property
    def children(self) -> Iterator['MonteCarloNode']:
        if not len(self._children): self._expand()
        return iter(self._children)
    

    def _expand(self) -> None:
        for new_state in self._state.expand_state():
            self._children.append(MonteCarloNode(new_state, self._c_coef, parent=self))

    def playouts(self) -> list[GameState]:
        return self._state.expand_state()

    def update(self, result: PlayerCharacter | Literal['T']):
        self._visits += 1
        if result == 'T': self._wins += .5
        elif self._state._play_char != result: self._wins += 1

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

        _backpropogate(leaf_node, simulation_result, kill_signal)
    return root

def _traversal(node: MonteCarloNode, kill_signal: list[bool]) -> MonteCarloNode:
    """Selection and expansion state in Monte Carlo Tree Search"""
    # selection
    while node.fully_expanded and (not kill_signal[0]):
        node = max(node.children, key=lambda child: child.uct)

    # expansion
    for child in node.children:
        if kill_signal[0]: return
        if not child.visits: return child

def _simulation(node: MonteCarloNode, kill_signal: list[bool]) -> PlayerCharacter | Literal['T']:
    """Simulation state in Monte Carlo Tree Search. Playout is selected randomly"""
    while not node.is_terminal and (not kill_signal[0]):
        node = rand.choice(list(node.children))

    return 'T' if (winner := get_winner(node._state._board_state)) is None else winner

def _backpropogate(node: MonteCarloNode, result: PlayerCharacter | Literal['T'], kill_signal: list[bool]) -> None:
    while node and (not kill_signal[0]):
        node.update(result)
        node = node.parent