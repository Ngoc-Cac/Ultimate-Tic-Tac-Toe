"""Contains the MainWindow widget and the home tab"""

from functools import wraps


from PyQt6.QtCore import QThreadPool
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTabWidget
)

from data_container.gamedata import GameData

from GUI.bot_process import BotProcess
from GUI.home_tab import Home
from GUI.tictactoe_board import (
    TicTacToe,
    UltimateTicTacToe
)
from GUI.rules_tab import Rules


from typing import Literal

import logging
logger = logging.getLogger(__name__)
### X ALWAYS GOES FIRST!!!
### if bot mode, who wins gets to go first

INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)

SCREEN_SIZE = (800, 600)
    

def undo_decor(undo_func):
    @wraps(undo_func)
    def undo_inner(*args, **kwargs):
        if not current_task.isFinished:
            # if bot is searching, no undo
            return

        if current_state.gametype == 'Ultimate':
            var_to_use = current_state.game
        else:
            var_to_use = current_state.game.boards[1][1]
        if (not len(current_state.prev_states)) or var_to_use.get_winner(): return

        if (current_state.gamemode == 'Bot') and (len(current_state.prev_states) > 1):
            undo_func()
            undo_func()
        elif (current_state.gamemode != 'Bot'):
            undo_func()
    return undo_inner

def board_cleanup():
    current_state.game.overlay_label.setHidden(True)

    if current_state.current_board:
        current_state.game\
                     .boards[current_state.current_board[0]]\
                            [current_state.current_board[1]]\
                     .focus_board(False)
        current_state.current_board = None

    for i, row in enumerate(current_state.game.boards):
        for j, board in enumerate(row):
            if (i == j == 1) or (current_state.gametype != 'Normal'):
                board.reset()

def restart():
    if not current_task.isFinished: current_task.stop()

    current_state.prev_states.clear()
    current_state.x_turn = True

    if current_state.gamemode == 'Bot':
        winner = current_state.game.get_winner(current_state.gametype)
        if winner in 'OT': current_state.bot_goes_first = not current_state.bot_goes_first

    board_cleanup()

    if (current_state.gamemode == 'Bot') and current_state.bot_goes_first: bot_move()

@undo_decor
def undo_move():
    prev_state = current_state.prev_states.pop()
    current_state.game.boards[prev_state[0][0]][prev_state[0][1]].focus_board(False)

    if prev_state[1].get_winner(): prev_state[1].reset_winner()
    prev_state[1].buttons[prev_state[0][0]][prev_state[0][1]].setText('')
    prev_state[1].buttons[prev_state[0][0]][prev_state[0][1]].setDisabled(False)

    if len(current_state.prev_states) and current_state.gametype == 'Ultimate':
        prev_state[1].focus_board()
        current_state.current_board = prev_state[1].position
    else: current_state.current_board = None
    current_state.x_turn = not current_state.x_turn

def play_turn(position: tuple[int, int], board: TicTacToe) -> None:
    if current_state.current_board and current_state.current_board != board.position: return

    board.buttons[position[0]][position[1]].setText('X' if current_state.x_turn else 'O')
    board.buttons[position[0]][position[1]].setDisabled(True)
    board.focus_board(False)
    current_state.x_turn = not current_state.x_turn

    if (temp := board.get_winner()):
        board.show_winner(temp)
    if (temp := current_state.game.get_winner(current_state.gamemode)):
        current_state.game.show_winner(temp)
        return
    
    current_state.prev_states.append((position, board))
    if current_state.game.boards[position[0]][position[1]].overlay_label.isHidden():
        current_state.game.boards[position[0]][position[1]].focus_board(current_state.gametype != 'Normal')
        current_state.current_board = position
    else: current_state.current_board = None

    if (current_state.gamemode == 'Bot') and (
            (current_state.bot_goes_first and current_state.x_turn) or\
            (not current_state.bot_goes_first and not current_state.x_turn)
       ):
        bot_move()

def bot_move():
    # make_move does the button click, the task just find the button to click
    # when the task is running, aboutToQuit signal is connected to the task stop process
    # this is so that when the program closes, the task is killed
    current_state.game.block_clicks(True)
    threadpool.start(current_task)


def _bot_click_button(button_to_click: QPushButton | None, task: BotProcess):
    current_state.game.block_clicks(False)

    if button_to_click: button_to_click.click()


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.setWindowTitle("Ultimate Tic-Tac-Toe")
        self.setGeometry(350, 100, *SCREEN_SIZE)
        self.setFixedSize(*SCREEN_SIZE)

        self.init_gametasks(app)
        self.setCentralWidget(self.init_tabs())


    def init_tabs(self) -> QTabWidget:
        tab_wid = QTabWidget()
        self.home_tab = Home(self.game, SCREEN_SIZE)
        self.home_tab.gamemode_changed.connect(self.change_gamemode)
        self.home_tab.gametype_changed.connect(self.change_gametype)
        self.home_tab.first_turn_changed.connect(self.change_turn)
        self.home_tab.bot_algo_changed.connect(self.change_bot_algo)
        self.home_tab.game_about_to_start.connect(self.start_game)
        self.home_tab.restart_signal.connect(restart)
        self.home_tab.undo_signal.connect(undo_move)

        tab_wid.addTab(Rules(), 'Rules and Info')
        tab_wid.addTab(self.home_tab, 'Play')

        tab_wid.setCurrentIndex(1)
        tab_wid.currentChanged.connect(self.change_tab_process)
        return tab_wid

    def init_gametasks(self, app: QApplication):
        global threadpool, current_task, application, current_state
        application = app

        self.game = UltimateTicTacToe(play_turn)
        current_state = GameData(self.game)

        threadpool = QThreadPool()
        current_task = BotProcess(current_state)
        current_task.signals.output.connect(_bot_click_button)
        application.aboutToQuit.connect(current_task.terminate)


    def change_tab_process(self, cur_index: int):
        if (cur_index == 1) and self.home_tab.overlay_menu['new'].isHidden():
            self.home_tab.overlay_menu['in-game'].setHidden(False)

    def change_gamemode(self, text: Literal['Human', 'Bot']):
        current_state.gamemode = text
    
    def change_gametype(self, text: Literal['Normal', 'Ultimate']):
        current_state.gametype = text

    def change_turn(self, text: Literal['Bot', 'Human']):
        current_state.bot_goes_first = bool(text == 'Bot')

    def change_bot_algo(self, text: Literal['Minimax', 'Monte Carlo Tree Search']):
        current_state.bot_algo = 'minimax' if text == 'Minimax' else 'monte_carlo'

    def start_game(self, new_game: bool):
        if not current_task.isFinished:
            # if the bot is currently searching, stop it
            current_task.stop()

        # make new game but no ongoing game
        if new_game and not current_state.game_ongoing:
            current_state.game.switch_mode(current_state.gametype)
            current_state.game_ongoing = True
            if (current_state.gamemode == 'Bot') and current_state.bot_goes_first:
                bot_move()
        # make new game but there is ongoing game
        elif new_game and current_state.game_ongoing:
            current_state.game_ongoing = False
            current_state.x_turn = True
            current_state.bot_goes_first = self.home_tab\
                                               .overlay_menu['new']\
                                               .choose_turn_butt.text() == 'Bot goes first!'
            board_cleanup()
        # continue ongoing game
        else:
            current_state.game_ongoing = True