from math import inf

from minimax.gamestate import GameState, UltimateGameState

# type import
from typing import Optional
from minimax.gamestate import TicTacToeBoard, UltimateTicTacToeBoard, PlayerCharacter

def minimax(game_state: GameState | UltimateGameState,
            maximizing: bool = True, *,
            max_depth: Optional[int] = None,
            **kwargs)\
            -> tuple[int, tuple[int, int]]:
    depth = kwargs['depth'] if 'depth' in kwargs else 0

    score = game_state.calculate_score()
    if not (score is None):
        return score - depth
    elif (not max_depth is None) and (depth >= max_depth):
        return game_state.heuristic_score(depth)

    alpha = kwargs['alpha'] if 'alpha' in kwargs else -inf
    beta = kwargs['beta'] if 'beta' in kwargs else inf

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
                        alpha=alpha, beta=beta, depth=depth + 1,
                        max_depth=max_depth)
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

def find_move_normal(board: TicTacToeBoard, turn: PlayerCharacter)\
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

def find_move_ultimate(main_board: UltimateTicTacToeBoard,
                       subboards: list[TicTacToeBoard],
                       turn: PlayerCharacter,
                       board_to_play: tuple[int, int] = None, *,
                       max_depth: int = 1000)\
    -> Optional[UltimateGameState]:
    state = UltimateGameState(main_board, subboards, turn, turn,
                              board_to_play=board_to_play)
    best_score = -inf
    best_state = None
    debug_i = 0
    for new_state in state.expand_state():
        print(f"{(debug_i := debug_i + 1)} states explored.")
        score = minimax(new_state, False, max_depth=max_depth)
        if best_score < score:
            best_state = new_state
            best_score = score
    return best_state