from PyQt6.QtCore import (
    QObject,
    QRunnable,
    pyqtSignal,
    pyqtSlot
)
from PyQt6.QtWidgets import QPushButton

from bot.gamestate import (
    GameState,
    UltimateGameState
)
from bot.mcts import (
    MonteCarloNode,
    monte_carlo_search
)
from bot.minimax import (
    find_move_normal,
    find_move_ultimate
)

from data_container.gamedata import GameData

from GUI.tictactoe_board import UltimateTicTacToe

from typing import (
    Literal,
    Optional
)


import logging
logger = logging.getLogger(__name__)


class BotSignals(QObject):
    output=pyqtSignal(object, object)

class BotProcess(QRunnable):
    def __init__(self, main_state: GameData):
        super().__init__()
        self.main_state = main_state
        self.kill_signal: list[bool] = [False]
        self.signals = BotSignals()
        self._isFinished = True
        self.terminate_sig = False

        self.setAutoDelete(False)

    @pyqtSlot()
    def run(self):
        self._isFinished = False
        self.kill_signal[0] = False
        butt_to_click = _search_move(self.main_state.gametype,
                                     self.main_state.game,
                                     self.main_state.x_turn,
                                     self.main_state.current_board,
                                     algorithm_to_use=self.main_state.bot_algo,
                                     kill_signal=self.kill_signal)

        if self.terminate_sig: return
        self.signals.output.emit(None if self.kill_signal[0] else butt_to_click, self)
        self._isFinished = True

    @property
    def isFinished(self):
        return self._isFinished
    
    def stop(self):
        self.kill_signal[0] = True

    def terminate(self):
        self.kill_signal[0] = True
        self.terminate_sig = True


def _search_move(gametype: Literal['Ultimate', 'Normal'],
                 game: UltimateTicTacToe, x_turn: bool,
                 current_board: tuple[int, int], *,
                 algorithm_to_use: Literal['minimax', 'monte_carlo'],
                 kill_signal: Optional[list[bool]] = None)\
    -> Optional[QPushButton]:
    if kill_signal is None: kill_signal = [False]

    turn = 'X' if x_turn else 'O'
    if gametype == 'Normal':
        board = game.boards[1][1].get_state()

        if algorithm_to_use == 'minimax':
            logger.info('Running minimax...')
            temp = find_move_normal(board, turn, kill_signal=kill_signal)
        else:
            logger.info('Running monte carlo...')
            temp = monte_carlo_search(MonteCarloNode(GameState(board, turn)),
                                      max_iter=2000, kill_signal=kill_signal)
            temp = None if temp is None else max(temp.children, key=lambda child: child.visits)._state

        if temp is None: return
        b2p_row, b2p_col, row, col = 1, 1, *temp.previous_move
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

        if algorithm_to_use == 'minimax':
            logger.info('Running minimax...')
            temp = find_move_ultimate(game.get_state(), subboards,
                                      turn=turn,
                                      board_to_play=current_board,
                                      max_depth=4,
                                      kill_signal=kill_signal)
        else:
            logger.info('Running monte carlo...')
            root = UltimateGameState(game.get_state(), subboards, turn,
                                     board_to_play=current_board)
            temp = monte_carlo_search(MonteCarloNode(root), max_iter=300,
                                      kill_signal=kill_signal)
            temp = None if temp is None else max(temp.children, key=lambda child: child.visits)._state
            
        if temp is None: return
        b2p_row, b2p_col, row, col = temp.previous_move
    return game.boards[b2p_row][b2p_col].buttons[row][col]