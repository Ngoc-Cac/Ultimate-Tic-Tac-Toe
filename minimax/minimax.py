from math import inf

from minimax.gamestate import GameState

# type import
from typing import Optional
from minimax.gamestate import TicTacToeBoard, PlayerCharacter

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