from math import inf
from copy import deepcopy

from typing import TypeAlias, Union, Literal, Optional

PlayerCharacter: TypeAlias = Literal['X', 'O']
TicTacToeBoard: TypeAlias = list[list[PlayerCharacter]]

NumericType: TypeAlias = Union[int, float]


EMPTY_CHAR: str = ' '
MAX_SCORE: int = 1000
class GameState():
    
    __slots__ = '_board_state', '_play_char', '_free_cells', '_previous_move', '_max_player'
    def __init__(self, board_state: TicTacToeBoard, player_char: PlayerCharacter,
                 max_player: PlayerCharacter, *,
                 free_cells: set[tuple[int, int]] = None,
                 previous_move: Optional[tuple[int, int]] = None):
        # Type check stuff please

        self._board_state = board_state
        self._play_char = player_char
        self._max_player = max_player
        self._previous_move = previous_move

        if free_cells is None:
            free_cells = set((i, j) for i, row in enumerate(self._board_state)
                                    for j, cell in enumerate(row)
                                    if cell == EMPTY_CHAR)
        self._free_cells = free_cells

    @property
    def previous_move(self) -> tuple[int, int]:
        return self._previous_move


    def expand_state(self) -> list['GameState']:
        new_states: list[GameState] = []
        for pos in self._free_cells:
            next_board = deepcopy(self._board_state)
            next_board[pos[0]][pos[1]] = self._play_char
            next_play_char = 'X' if self._play_char != 'X' else 'O'

            new_states.append(GameState(next_board, next_play_char,
                                        self._max_player,
                                        free_cells=self._free_cells - {pos},
                                        previous_move=pos))
        return new_states

    def calculate_score(self) -> Optional[NumericType]:
        main_diag = []
        sub_diag = []
        for i, row in enumerate(self._board_state):
            # rows
            row_alias = set(row)
            if (not EMPTY_CHAR in row_alias) and (len(row_alias) == 1):
                return MAX_SCORE if self._max_player in row_alias else -MAX_SCORE
            # cols
            col = set(cell[i] for cell in self._board_state)
            if (not EMPTY_CHAR in col) and (len(col) == 1):
                return MAX_SCORE if self._max_player in col else -MAX_SCORE

            main_diag.append(row[i])
            sub_diag.append(self._board_state[2 - i][i])

        main_diag = set(main_diag)
        sub_diag = set(sub_diag)
        if (not EMPTY_CHAR in main_diag) and len(main_diag) == 1:
            return MAX_SCORE if self._max_player in main_diag else -MAX_SCORE
        if (not EMPTY_CHAR in sub_diag) and len(sub_diag) == 1:
            return MAX_SCORE if self._max_player in sub_diag else -MAX_SCORE
        # tie
        if not len(self._free_cells): return 0
        return None

    def __str__(self) -> str:
        return '\n'.join('|'.join(row) for row in self._board_state)

def minimax(game_state: GameState, maximizing: bool = True, *,
            alpha = -inf, beta = inf, depth: int = 0)\
            -> tuple[int, tuple[int, int]]:
    score = game_state.calculate_score()
    if not (score is None):
        return score - depth

    if maximizing:
        score, optimise_func = -inf, max
        alpha_beta_check = lambda score: score > beta
        def update_ab(value):
            nonlocal alpha
            alpha = optimise_func(alpha, value)
    else:
        score, optimise_func = inf, min
        alpha_beta_check = lambda score: score < alpha
        def update_ab(value):
            nonlocal beta
            beta = optimise_func(beta, value)

    for neighbour in game_state.expand_state():
        recur = minimax(neighbour, not maximizing,
                        alpha=alpha, beta=beta, depth=depth + 1)
        score = optimise_func(score, recur)
        update_ab(score)
        if alpha_beta_check(score): break
    return score
### raw implementation, no alpha-beta
# def minimax(game_state: GameState, maximizing: bool = True, *,
#             depth: int = 0)\
#             -> tuple[int, tuple[int, int]]:
#     score = game_state.calculate_score()
#     if not (score is None):
#         return score - depth

#     if maximizing:
#         score, optimise_func = -inf, max
#     else:
#         score, optimise_func = inf, min

#     for neighbour in game_state.expand_state():
#         recur = minimax(neighbour, not maximizing, depth=depth + 1)
#         score = optimise_func(score, recur)
#     return score

def find_move(board: TicTacToeBoard, turn: PlayerCharacter)\
    -> Optional[GameState]:
    state = GameState(board, turn, turn)
    best_score = -inf
    best_state = None
    for new_state in state.expand_state():
        score = minimax(new_state, False)
        if best_score < score:
            best_state = new_state
            best_score = score
    return best_state


### TESTING ZONE ###
def test():
    state = [[' ', ' ', 'X'],
             [' ', ' ', ' '],
             [' ', ' ', ' ']]
    bot = 'O'
    finished = find_move(state, bot)
    print(finished)
    # test = GameState(state, bot, bot)
    # neighbours = test.expand_state()
    # index = 4
    # print(neighbours[index])
    # print(minimax(neighbours[index], False))
    # print(neighbours[index].calculate_score())

if __name__ == '__main__':
    test()