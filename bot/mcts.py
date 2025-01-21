import math
import random as rand

from bot.gamestate import GameState, get_winner

from typing import Iterator, Optional, Literal
from bot.gamestate import PlayerCharacter

class MonteCarloNode:
    __slots__ = '_state', '_visits', '_wins',\
                '_c_coef',\
                '_children', '_parent'
    def __init__(self, state: GameState, c_coefficient: float = math.sqrt(2), **kwargs):
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

    def update(self, result: PlayerCharacter | Literal['T']):
        self._visits += 1
        if result == 'T': self._wins += .5
        elif self._state._play_char != result: self._wins += 1

def monte_carlo_search(root: MonteCarloNode, max_iter: int = 1000) -> MonteCarloNode:
    i = -1
    while (i := i + 1) < max_iter:
        leaf_node = _traversal(root)

        # the game has ended
        if leaf_node is None: continue
        simulation_result = _simulation(leaf_node)

        _backpropogate(leaf_node, simulation_result)
    return root

def _traversal(node: MonteCarloNode) -> MonteCarloNode:
    # selection
    while node.fully_expanded:
        node = max(node.children, key=lambda child: child.uct)

    # expansion
    for child in node.children:
        if not child.visits: return child

def _simulation(node: MonteCarloNode) -> PlayerCharacter | Literal['T']:
    while not node.is_terminal:
        node = rand.choice(list(node.children))
    return node.winner

def _backpropogate(node: MonteCarloNode, result: PlayerCharacter | Literal['T']) -> None:
    while node:
        node.update(result)
        node = node.parent