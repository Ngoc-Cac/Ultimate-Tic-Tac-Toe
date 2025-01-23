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

x_turn: bool = True
current_board: Optional[tuple[int, int]] = None
# previous state contains: previous position played, the previous board
# that was played on
prev_states: list[tuple[tuple[int, int], 'TicTacToe']] = []

bot_goes_first: bool = True
game_ongoing: bool = False
gametype: Literal['Normal', 'Ultimate'] = 'Ultimate'
gamemode: Literal['Human', 'Bot'] = 'Human'

bot_algo: Literal['minimax', 'monte_carlo'] = 'monte_carlo'

INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)

SCREEN_SIZE = (800, 600)
    

def undo_decor(undo_func):
    @wraps(undo_func)
    def undo_inner(*args, **kwargs):
        if not current_task.isFinished:
            # if bot is searching, no undo
            return

        var_to_use = game if gametype == 'Ultimate' else game.boards[1][1]
        if (not len(prev_states)) or var_to_use.get_winner(): return

        if (gamemode == 'Bot') and (len(prev_states) > 1):
            undo_func()
            undo_func()
        elif (gamemode != 'Bot'):
            undo_func()
    return undo_inner

def board_cleanup():
    global current_board
    game.overlay_label.setHidden(True)

    if current_board:
        game.boards[current_board[0]][current_board[1]].focus_board(False)
        current_board = None

    for i, row in enumerate(game.boards):
        for j, board in enumerate(row):
            if (i == j == 1) or (gametype != 'Normal'):
                board.reset()

def restart():
    global x_turn, bot_goes_first
    if not (current_task is None or current_task.isFinished): current_task.stop()

    prev_states.clear()
    x_turn = True

    if gamemode == 'Bot':
        winner = game.boards[1][1].get_winner() if gametype == 'Normal' else game.get_winner()
        if winner in 'OT': bot_goes_first = not bot_goes_first

    board_cleanup()

    if (gamemode == 'Bot') and bot_goes_first: bot_move()

@undo_decor
def undo_move():
    global x_turn, current_board
    
    prev_state = prev_states.pop()
    game.boards[prev_state[0][0]][prev_state[0][1]].focus_board(False)

    if prev_state[1].get_winner(): prev_state[1].reset_winner()
    prev_state[1].buttons[prev_state[0][0]][prev_state[0][1]].setText('')
    prev_state[1].buttons[prev_state[0][0]][prev_state[0][1]].setDisabled(False)

    if len(prev_states) and gametype == 'Ultimate':
        prev_state[1].focus_board()
        current_board = prev_state[1].position
    else: current_board = None
    x_turn = not x_turn

def play_turn(position: tuple[int, int], board: TicTacToe) -> None:
    global x_turn, current_board
    if current_board and current_board != board.position: return

    board.buttons[position[0]][position[1]].setText('X' if x_turn else 'O')
    board.buttons[position[0]][position[1]].setDisabled(True)
    board.focus_board(False)
    x_turn = not x_turn

    if (temp := board.get_winner()):
        board.show_winner(temp)
    if (temp := game.get_winner()):
        game.show_winner(temp)
        return
    
    prev_states.append((position, board))
    if game.boards[position[0]][position[1]].overlay_label.isHidden():
        game.boards[position[0]][position[1]].focus_board(gametype != 'Normal')
        current_board = position
    else: current_board = None

    if (gamemode == 'Bot') and (
            (bot_goes_first and x_turn) or\
            (not bot_goes_first and not x_turn)
       ):
        bot_move()

def bot_move():
    # make_move does the button click, the task just find the button to click
    # when the task is running, aboutToQuit signal is connected to the task stop process
    # this is so that when the program closes, the task is killed
    global current_task
    game.block_clicks(True)

    current_task = BotProcess(gametype, game, x_turn, current_board,
                              algorithm_to_use=bot_algo)
    current_task.signals.output.connect(_bot_click_button)
    application.aboutToQuit.connect(current_task.terminate)

    threadpool.start(current_task)

def _bot_click_button(button_to_click: QPushButton | None, task: BotProcess):
    # however, to avoid multiple connections to task that has stopped running,
    # everytime the task finishes, the signal is then disconnected
    application.aboutToQuit.disconnect(task.terminate)
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
        global gamemode
        gamemode = text
        self.overlay_menu['new'].choose_turn_butt.setHidden(text == 'Human')
    
    def change_gametype(self, text: Literal['Normal', 'Ultimate']):
        global gametype
        gametype = text

    def change_turn(self):
        global bot_goes_first
        bot_goes_first = not bot_goes_first
        subject = 'Bot' if bot_goes_first else 'Human'
        self.overlay_menu['new'].choose_turn_butt.setText(subject + ' goes first!')

    def change_bot_algo(self, text: Literal['Minimax', 'Monte Carlo Tree Search']):
        global bot_algo
        bot_algo = 'minimax' if text == 'Minimax' else 'monte_carlo'

    def ingame_menu_popup(self, tab_index: int):
        if tab_index == 0:
            self.overlay_menu['in-game'].setHidden(False)
        elif tab_index == 1:
            self.overlay_menu['settings'].setHidden(False)


    def start_game(self, new_game: bool):
        global game_ongoing, x_turn, bot_goes_first
        if not (current_task is None or current_task.isFinished):
            # if the bot is currently searching, stop it
            current_task.stop()

        # make new game but no ongoing game
        if new_game and not game_ongoing:
            game.switch_mode(gametype)
            game_ongoing = True
            self.overlay_menu['new'].setHidden(True)
            if (gamemode == 'Bot') and bot_goes_first:
                bot_move()
        # make new game but there is ongoing game
        elif new_game and game_ongoing:
            game_ongoing = False
            x_turn = True
            bot_goes_first = self.overlay_menu['new'].choose_turn_butt.text() == 'Bot goes first!'
            board_cleanup()
            self.overlay_menu['new'].setHidden(False)
        # continue ongoing game
        else:
            game_ongoing = True

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

        global threadpool, current_task, application
        threadpool = QThreadPool()
        current_task = BotProcess(gametype, game, x_turn, current_board,
                                  algorithm_to_use=bot_algo)
        application = app