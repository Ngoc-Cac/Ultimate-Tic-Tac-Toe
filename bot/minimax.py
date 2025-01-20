from math import inf

from bot.gamestate import GameState, UltimateGameState

# type import
from typing import Optional

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