"""Contains the MainWindow widget and the home tab"""

from functools import wraps


from PyQt6.QtCore import (
    Qt,
    QThreadPool,
    QSize
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStyle,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget
)


from GUI.bot_process import BotProcess
from GUI.gamedata import GameData
from GUI.menus import (
    InGameMenu,
    NewGameMenu,
    SettingsMenu
)
from GUI.tictactoe_board import (
    TicTacToe,
    UltimateTicTacToe
)
from GUI.rules_tab import Rules


from typing import (
    Literal,
    Optional
)
### X ALWAYS GOES FIRST!!!
### if bot mode, who wins gets to go first

# @dataclass
# class MainState():
#     x_turn: bool = True
#     current_board: Optional[tuple[int, int]] = None
#     # previous state contains: previous position played, the previous board
#     # that was played on
#     prev_states: list[tuple[tuple[int, int], TicTacToe]] = field(default_factory=lambda: [])

#     bot_goes_first: bool = True
#     game_ongoing: bool = False
#     gametype: Literal['Normal', 'Ultimate'] = 'Ultimate'
#     gamemode: Literal['Human', 'Bot'] = 'Human'

#     bot_algo: Literal['minimax', 'monte_carlo'] = 'monte_carlo'

INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)

SCREEN_SIZE = (800, 600)
    

def undo_decor(undo_func):
    @wraps(undo_func)
    def undo_inner(*args, **kwargs):
        if not current_task.isFinished:
            # if bot is searching, no undo
            return

        var_to_use = game if current_state.gametype == 'Ultimate' else game.boards[1][1]
        if (not len(current_state.prev_states)) or var_to_use.get_winner(): return

        if (current_state.gamemode == 'Bot') and (len(current_state.prev_states) > 1):
            undo_func()
            undo_func()
        elif (current_state.gamemode != 'Bot'):
            undo_func()
    return undo_inner

def board_cleanup():
    game.overlay_label.setHidden(True)

    if current_state.current_board:
        game.boards[current_state.current_board[0]][current_state.current_board[1]].focus_board(False)
        current_state.current_board = None

    for i, row in enumerate(game.boards):
        for j, board in enumerate(row):
            if (i == j == 1) or (current_state.gametype != 'Normal'):
                board.reset()

def restart():
    if not current_task.isFinished: current_task.stop()

    current_state.prev_states.clear()
    current_state.x_turn = True

    if current_state.gamemode == 'Bot':
        winner = game.boards[1][1].get_winner() if current_state.gametype == 'Normal' else game.get_winner()
        if winner in 'OT': current_state.bot_goes_first = not current_state.bot_goes_first

    board_cleanup()

    if (current_state.gamemode == 'Bot') and current_state.bot_goes_first: bot_move()

@undo_decor
def undo_move():
    prev_state = current_state.prev_states.pop()
    game.boards[prev_state[0][0]][prev_state[0][1]].focus_board(False)

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
    if (temp := game.get_winner()):
        game.show_winner(temp)
        return
    
    current_state.prev_states.append((position, board))
    if game.boards[position[0]][position[1]].overlay_label.isHidden():
        game.boards[position[0]][position[1]].focus_board(current_state.gametype != 'Normal')
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
    game.block_clicks(True)
    threadpool.start(current_task)


def _bot_click_button(button_to_click: QPushButton | None, task: BotProcess):
    game.block_clicks(False)

    if button_to_click: button_to_click.click()

    task.finish()


class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.init_gamezone()
        self.init_menus()

    def init_menus(self):
        bg_color = "background-color: rgba(0, 0, 0, 170)"
        self.overlay_menu: dict[Literal['new', 'in-game'], QFrame] = {}
        self.overlay_menu['new'] = NewGameMenu(self)
        self.overlay_menu['new'].play_button.clicked.connect(lambda: self.start_game(True))
        self.overlay_menu['new'].gametype_box.currentTextChanged.connect(self.change_gametype)
        self.overlay_menu['new'].mode_box.currentTextChanged.connect(self.change_gamemode)
        self.overlay_menu['new'].choose_turn_butt.clicked.connect(self.change_turn)

        self.overlay_menu['in-game'] = InGameMenu(self)
        self.overlay_menu['in-game'].continue_butt.clicked.connect(lambda: self.start_game(False))
        self.overlay_menu['in-game'].new_game_butt.clicked.connect(lambda: self.start_game(True))
        self.overlay_menu['in-game'].setHidden(True)

        self.overlay_menu['settings'] = SettingsMenu(self)
        self.overlay_menu['settings'].continue_butt.clicked.connect(lambda: self.start_game(False))
        self.overlay_menu['settings'].algo_box.currentTextChanged.connect(self.change_bot_algo)
        self.overlay_menu['settings'].setHidden(True)


        self.overlay_menu['new'].setStyleSheet(bg_color)
        self.overlay_menu['in-game'].setStyleSheet(bg_color)
        self.overlay_menu['settings'].setStyleSheet(bg_color)

        self.overlay_menu['new'].setFixedSize(*SCREEN_SIZE)
        self.overlay_menu['in-game'].setFixedSize(*SCREEN_SIZE)
        self.overlay_menu['settings'].setFixedSize(*SCREEN_SIZE)

    def init_gamezone(self) -> None:
        global game
        game = UltimateTicTacToe(play_turn)


        hamburg_ico = QWidget().style()\
                               .standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        settings_ico = QWidget().style()\
                                .standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        tabbar = QTabBar(self)
        tabbar.setDrawBase(False)
        tabbar.setFixedSize(200, 50)
        tabbar.setIconSize(QSize(25, 25))

        tabbar.addTab(hamburg_ico, None)
        tabbar.addTab(settings_ico, None)
        tabbar.tabBarClicked.connect(self.ingame_menu_popup)
        

        reset_button = QPushButton('Restart')
        reset_button.setFixedSize(70, 30)
        reset_button.clicked.connect(restart)

        undo_button = QPushButton('Undo')
        undo_button.setFixedSize(60, 30)
        undo_button.clicked.connect(undo_move)


        hbox = QHBoxLayout()
        hbox.addWidget(undo_button)
        hbox.addWidget(reset_button)
        hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(game)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(vbox)


    def change_gamemode(self, text: Literal['Human', 'Bot']):
        current_state.gamemode = text
        self.overlay_menu['new'].choose_turn_butt.setHidden(text == 'Human')
    
    def change_gametype(self, text: Literal['Normal', 'Ultimate']):
        current_state.gametype = text

    def change_turn(self):
        current_state.bot_goes_first = not current_state.bot_goes_first
        subject = 'Bot' if current_state.bot_goes_first else 'Human'
        self.overlay_menu['new'].choose_turn_butt.setText(subject + ' goes first!')

    def change_bot_algo(self, text: Literal['Minimax', 'Monte Carlo Tree Search']):
        current_state.bot_algo = 'minimax' if text == 'Minimax' else 'monte_carlo'

    def ingame_menu_popup(self, tab_index: int):
        if tab_index == 0:
            self.overlay_menu['in-game'].setHidden(False)
        elif tab_index == 1:
            self.overlay_menu['settings'].setHidden(False)


    def start_game(self, new_game: bool):
        if not current_task.isFinished:
            # if the bot is currently searching, stop it
            current_task.stop()

        # make new game but no ongoing game
        if new_game and not current_state.game_ongoing:
            game.switch_mode(current_state.gametype)
            current_state.game_ongoing = True
            self.overlay_menu['new'].setHidden(True)
            if (current_state.gamemode == 'Bot') and current_state.bot_goes_first:
                bot_move()
        # make new game but there is ongoing game
        elif new_game and current_state.game_ongoing:
            current_state.game_ongoing = False
            current_state.x_turn = True
            current_state.bot_goes_first = self.overlay_menu['new'].choose_turn_butt.text() == 'Bot goes first!'
            board_cleanup()
            self.overlay_menu['new'].setHidden(False)
        # continue ongoing game
        else:
            current_state.game_ongoing = True

        self.overlay_menu['in-game'].setHidden(True)
        self.overlay_menu['settings'].setHidden(True)


class Tabs(QTabWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.home_tab = Home()

        self.addTab(Rules(), 'Rules and Info')
        self.addTab(self.home_tab, 'Play')

        self.setCurrentIndex(1)
        self.currentChanged.connect(self.change_tab_process)

    def change_tab_process(self, cur_index: int):
        if (cur_index == 1) and self.home_tab.overlay_menu['new'].isHidden():
            self.home_tab.overlay_menu['in-game'].setHidden(False)

class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.setWindowTitle("Ultimate Tic-Tac-Toe")
        self.setGeometry(350, 100, *SCREEN_SIZE)
        self.setFixedSize(*SCREEN_SIZE)

        self.setCentralWidget(Tabs())

        global threadpool, current_task, application, current_state
        application = app
        current_state = GameData(game)
        threadpool = QThreadPool()
        current_task = BotProcess(current_state)
        current_task.signals.output.connect(_bot_click_button)
        application.aboutToQuit.connect(current_task.terminate)