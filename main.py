import random as rand
from functools import wraps

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as QtWidgets

from GUI.tictactoe_board import TicTacToe, UltimateTicTacToe
from GUI.menus import NewGameMenu, InGameMenu
from minimax.minimax import find_move
from minimax.gamestate import EMPTY_CHAR

from typing import Optional, Literal
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

INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)


def undo_decor(func):
    @wraps(func)
    def undo_inner(*args, **kwargs):
        var_to_use = game if gametype == 'Ultimate' else game.boards[1][1]
        if (not len(prev_states)) or var_to_use.get_winner(): return
        func()
        if gamemode == 'Bot': func()
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
       ): bot_move()

def bot_move():
    if gametype == 'Normal':
        board = [[cell if cell else EMPTY_CHAR for cell in row]
                for row in game.boards[1][1].get_state()]
        temp = find_move(board, 'X' if x_turn else 'O')

        if temp is None: return
        row, col = temp.previous_move
        button_to_click = game.boards[1][1].buttons[row][col]
    else:
        empty_cells = []
        if current_board:
            board_to_click = game.boards[current_board[0]][current_board[1]]
        else:
            board_to_click = rand.choice([board for row in game.boards for board in row
                                          if board.overlay_label.isHidden()])
        for row in board_to_click.buttons:
            for button in row:
                if not button.text():
                    empty_cells.append(button)
        button_to_click = rand.choice(empty_cells)

    button_to_click.click()



class Rules(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel(r"¯\_(ツ)_/¯", parent=self)

class Home(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_gamezone()
        self.init_menus()

    def init_menus(self):
        bg_color = "background-color: rgba(0, 0, 0, 170)"
        self.overlay_menu: dict[Literal['new', 'in-game'], QtWidgets.QFrame] = {}
        self.overlay_menu['new'] = NewGameMenu(self.start_game, self.change_gametype,
                                               self.change_gamemode, self.change_turn,
                                               self)
        self.overlay_menu['in-game'] = InGameMenu(lambda: self.start_game(False),
                                                  lambda: self.start_game(True),
                                                  self)
        self.overlay_menu['in-game'].setHidden(True)

        self.overlay_menu['new'].setStyleSheet(bg_color)
        self.overlay_menu['in-game'].setStyleSheet(bg_color)

        self.overlay_menu['new'].setFixedSize(*SCREEN_SIZE)
        self.overlay_menu['in-game'].setFixedSize(*SCREEN_SIZE)

    def init_gamezone(self) -> None:
        global game
        game = UltimateTicTacToe(play_turn)


        hamburger_butt = QtWidgets.QPushButton(self)
        hamburger_butt.clicked.connect(self.ingame_menu_popup)
        hamburger_butt.setFixedSize(50, 50)
        ico = hamburger_butt.style()\
                            .standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView)
        hamburger_butt.setIcon(ico)
        hamburger_butt.setIconSize(QSize(50, 50))

        reset_button = QtWidgets.QPushButton('New Game')
        reset_button.setFixedSize(80, 30)
        reset_button.clicked.connect(restart)

        undo_button = QtWidgets.QPushButton('Undo')
        undo_button.setFixedSize(50, 30)
        undo_button.clicked.connect(undo_move)


        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(undo_button)
        hbox.addWidget(reset_button)
        hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        vbox = QtWidgets.QVBoxLayout()
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
        for i, row in enumerate(game.boards):
            for j, board in enumerate(row):
                if i == j == 1: continue
                board.overlay_label.setText('')
                board.overlay_label.setHidden(text != 'Normal')

    def change_turn(self):
        global bot_goes_first
        bot_goes_first = not bot_goes_first
        subject = 'Bot' if bot_goes_first else 'Human'
        self.overlay_menu['new'].choose_turn_butt.setText(subject + ' goes first!')

    def ingame_menu_popup(self):
        self.overlay_menu['in-game'].setHidden(False)


    def start_game(self, new_game: bool):
        global game_ongoing, x_turn, bot_goes_first
        # make new game but no ongoing game
        if new_game and not game_ongoing:
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


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.home_tab = Home()

        self.addTab(Rules(), 'Rules and Info')
        self.addTab(self.home_tab, 'Play')
        # add settings tab?
        # self.addTab(Settings(), 'Settings')

        self.setCurrentIndex(1)
        self.currentChanged.connect(self.change_tab_process)

    def change_tab_process(self, cur_index: int):
        if (cur_index == 1) and self.home_tab.overlay_menu['new'].isHidden():
            self.home_tab.overlay_menu['in-game'].setHidden(False)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ultimate Tic-Tac-Toe")
        self.setGeometry(350, 100, *SCREEN_SIZE)
        self.setFixedSize(*SCREEN_SIZE)
        self.setCentralWidget(Tabs())



if __name__=="__main__":
    SCREEN_SIZE = (800, 600)

    ult_tictactoe = QtWidgets.QApplication([])
    root = MainWindow()
    root.show()
    ult_tictactoe.exec()