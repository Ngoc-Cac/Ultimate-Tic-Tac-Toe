from math import inf

from bot.gamestate import GameState, UltimateGameState

# type import
from typing import Optional
from bot.gamestate import TicTacToeBoard, UltimateTicTacToeBoard, PlayerCharacter, NumericType

def minimax(game_state: GameState | UltimateGameState,
            maximizing: bool = True, *,
            max_depth: Optional[int] = 20,
            **kwargs)\
            -> NumericType:
    """
    Minimax algorithm with alpha-beta pruning.

    ## Parameters:
    `game_state` (`GameState | UltimateGameState`): the root state to begin searching
    `maximizing` (`bool`): if current player is maximizing players
    `max_depth` (`int | None`): the maximum search depth. By default, this is 20. If there is no\
        limited depth, set `max_depth` to `None`. Note: be careful as this can lead to a StackOverflow.

    ## Return
    A number representing the score of the current state.
    """
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

def find_move_normal(board: TicTacToeBoard, turn: PlayerCharacter, *,
                     kill_signal: list[bool])\
    -> Optional[GameState]:
    """
    Find the best move from the current Tic-Tac-Toe board

    ## Parameters:
    `board`: the current Tic-Tac-Toe board
    `turn`: the player to make a move
    `kill_signal`: stopping condition. This should be a list of ONE bool value,\
        a list is not necessary, any mutable container can be replaced.

    ## Retun
    the GameState containing the next move to play, access this through the attribute `previous_move`.\
        Otherwise, if the current state can't be expanded, return `None`.
    """
    state = GameState(board, turn)
    best_score = -inf
    best_state = None
    for new_state in state.expand_state():
        if kill_signal[0]: break

        score = minimax(new_state, False)
        if best_score < score:
            best_state = new_state
            best_score = score
    return best_state

def find_move_ultimate(main_board: UltimateTicTacToeBoard,
                       subboards: list[TicTacToeBoard],
                       turn: PlayerCharacter,
                       board_to_play: tuple[int, int] = None, *,
                       kill_signal: list[bool],
                       max_depth: int = 20)\
    -> Optional[UltimateGameState]:
    """
    Find the best move from the current Ultimate Tic-Tac-Toe board

    ## Parameters:
    `main_board`: the current Ultimate Tic-Tac-Toe board
    `subboards`: a 3x3 grid of Tic-Tac-Toe boards
    `turn`: the player to make a move
    `board_to_play`: the subboard to play on
    `kill_signal`: stopping condition. This should be a list of ONE bool value,\
        a list is not necessary, any mutable container can be replaced.
    `max_depth`: maximum search depth

    ## Return
    the UltimateGameState containing the next move to play, access this through the\
        attribute `previous_move`. Otherwise, if the current state can't be expanded, return `None`.
    """
    state = UltimateGameState(main_board, subboards, turn,
                              board_to_play=board_to_play)
    best_score = -inf
    best_state = None
    for new_state in state.expand_state():
        if kill_signal[0]: break

        score = minimax(new_state, False, max_depth=max_depth)
        if best_score < score:
            best_state = new_state
            best_score = score
    return best_state