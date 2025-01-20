from math import inf

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QPushButton

from bot.minimax import minimax
from bot.gamestate import GameState, UltimateGameState
from GUI.tictactoe_board import UltimateTicTacToe

from typing import Literal, Optional
from bot.gamestate import TicTacToeBoard, UltimateTicTacToeBoard, PlayerCharacter


def find_move_normal(board: TicTacToeBoard, turn: PlayerCharacter, *,
                     kill_signal: list[bool])\
    -> Optional[GameState]:
    state = GameState(board, turn, turn)
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
                       max_depth: int = 1000,
                       kill_signal: list[bool])\
    -> Optional[UltimateGameState]:
    state = UltimateGameState(main_board, subboards, turn, turn,
                              board_to_play=board_to_play)
    best_score = -inf
    best_state = None
    debug_i = 0
    for new_state in state.expand_state():
        if kill_signal[0]: break

        print(debug_i := debug_i + 1)
        score = minimax(new_state, False, max_depth=max_depth)
        if best_score < score:
            best_state = new_state
            best_score = score
    return best_state


class BotSignals(QObject): # All Qt widgets inherit QObject.
    output=pyqtSignal(object, object)

class BotProcess(QRunnable):
    def __init__(self, gametype: Literal['Ultimate', 'Normal'],
                       game: UltimateTicTacToe, x_turn: bool,
                       current_board: Optional[tuple[int, int]]):
        super().__init__()
        self.args = [gametype, game, x_turn, current_board]
        self.kill_signal: list[bool] = [False]
        self.signals = BotSignals()
        self._isFinished = True

    @pyqtSlot()
    def run(self):
        self._isFinished = False
        butt_to_click = _search_move(*self.args, kill_signal=self.kill_signal)
        self.signals.output.emit(None if self.kill_signal[0] else butt_to_click, self)

    @property
    def isFinished(self):
        return self._isFinished
    
    def stop(self):
        self.kill_signal[0] = True

    def finish(self):
        self._isFinished = True



def _search_move(gametype: Literal['Ultimate', 'Normal'],
                 game: UltimateTicTacToe, x_turn: bool,
                 current_board: tuple[int, int], *,
                 kill_signal: Optional[list[bool]] = None)\
    -> Optional[QPushButton]:
    if kill_signal is None: kill_signal = [False]

    if gametype == 'Normal':
        board = game.boards[1][1].get_state()
        temp = find_move_normal(board, 'X' if x_turn else 'O',
                                kill_signal=kill_signal)

        if temp is None: return
        row, col = temp.previous_move
        button_to_click = game.boards[1][1].buttons[row][col]
    else:
        # empty_cells = []
        # if current_board:
        #     board_to_click = game.boards[current_board[0]][current_board[1]]
        # else:
        #     board_to_click = rand.choice([board for row in game.boards for board in row
        #                                   if board.overlay_label.isHidden()])
        # for row in board_to_click.buttons:
        #     for button in row:
        #         if not button.text():
        #             empty_cells.append(button)
        # button_to_click = rand.choice(empty_cells)

        subboards = []
        for row in game.boards:
            subboards.append([board.get_state() for board in row])
        temp = find_move_ultimate(game.get_state(), subboards,
                                  turn= 'X' if x_turn else 'O',
                                  board_to_play=current_board,
                                  max_depth=4,
                                  kill_signal=kill_signal)
        
        if temp is None: return
        b2p_row, b2p_col, row, col = temp.previous_move
        button_to_click = game.boards[b2p_row][b2p_col].buttons[row][col]

    return button_to_click