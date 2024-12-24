import random as rand
from functools import wraps

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as QtWidgets

from GUI.tictactoe_board import TicTacToe, UltimateTicTacToe
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

def restart():
    global current_board, x_turn, bot_goes_first
    prev_states.clear()
    x_turn = True

    if gamemode == 'Bot':
        winner = game.boards[1][1].get_winner() if gametype == 'Normal' else game.get_winner()
        if winner in 'OT': bot_goes_first = not bot_goes_first

    game.overlay_label.setHidden(True)

    if current_board:
        game.boards[current_board[0]][current_board[1]].focus_board(False)
        current_board = None

    for i, row in enumerate(game.boards):
        for j, board in enumerate(row):
            if (i == j == 1) or (gametype != 'Normal'):
                board.reset()

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
        self.init_menu()

    def init_menu(self):
        bg_color = "background-color: rgba(0, 0, 0, 170)"
        transparent_bg = "background-color: transparent"
        self.overlay_menu = {'new': QtWidgets.QWidget(self),
                             'in-game': QtWidgets.QWidget(self)}
        
        self.overlay_menu['new'].setStyleSheet(bg_color)
        self.overlay_menu['in-game'].setStyleSheet(bg_color)
        self.overlay_menu['in-game'].setHidden(True)

        self.overlay_menu['new'].setFixedSize(*SCREEN_SIZE)
        self.overlay_menu['in-game'].setFixedSize(*SCREEN_SIZE)
        

        # new game menu
        vbox = QtWidgets.QVBoxLayout()

        ## game type choosing zone
        gametype_hbox = self.init_gametype_zone()
        
        ## mode choosing zone
        mode_hbox = self.init_gamemode_zone()

        ## play button zone
        play_button = QtWidgets.QPushButton('Play!')
        play_button.clicked.connect(lambda: self.start_game(new_game=True))
        play_button.setStyleSheet(transparent_bg)
        play_button.setFont(INFO_FONT)
        play_button.setFixedSize(100, 50)

        vbox.addLayout(gametype_hbox)
        vbox.addLayout(mode_hbox)
        vbox.addWidget(play_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_menu['new'].setLayout(vbox)

    def init_gametype_zone(self):
        transparent_bg = "background-color: transparent"

        gametype_box = QtWidgets.QComboBox()
        gametype_box.addItems(['Normal', 'Ultimate'])
        gametype_box.setCurrentIndex(1)
        gametype_box.setStyleSheet(transparent_bg)
        gametype_box.setFont(INFO_FONT)
        gametype_box.setFixedSize(115, 50)
        gametype_box.currentTextChanged.connect(self.change_gametype)

        decorative_label = QtWidgets.QLabel('Game Type:')
        decorative_label.setStyleSheet(transparent_bg)
        decorative_label.setFont(INFO_FONT)
        decorative_label.setFixedSize(110, 30)
        decorative_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        gametype_hbox = QtWidgets.QHBoxLayout()
        gametype_hbox.addWidget(decorative_label)
        gametype_hbox.addWidget(gametype_box)
        gametype_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return gametype_hbox

    def init_gamemode_zone(self):
        transparent_bg = "background-color: transparent"

        mode_box = QtWidgets.QComboBox()
        mode_box.addItems(['Human', 'Bot'])
        mode_box.setStyleSheet(transparent_bg)
        mode_box.setFont(INFO_FONT)
        mode_box.setFixedSize(115, 50)
        mode_box.currentTextChanged.connect(self.change_gamemode)

        
        self.choose_turn_butt = QtWidgets.QPushButton('Bot goes first!')
        self.choose_turn_butt.setFont(INFO_FONT)
        self.choose_turn_butt.setHidden(True)
        self.choose_turn_butt.setFixedSize(200, 50)
        self.choose_turn_butt.setStyleSheet(transparent_bg)
        self.choose_turn_butt.clicked.connect(self.change_turn)

        decorative_label = QtWidgets.QLabel('Mode:')
        decorative_label.setStyleSheet(transparent_bg)
        decorative_label.setFont(INFO_FONT)
        decorative_label.setFixedSize(110, 30)
        decorative_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        mode_hbox = QtWidgets.QHBoxLayout()
        mode_hbox.addWidget(decorative_label)
        mode_hbox.addWidget(mode_box)
        mode_hbox.addWidget(self.choose_turn_butt)
        mode_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return mode_hbox


    def init_gamezone(self) -> None:
        global game
        game = UltimateTicTacToe(play_turn)


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
        self.choose_turn_butt.setHidden(text == 'Human')
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
        self.choose_turn_butt.setText(subject + ' goes first!')


    def start_game(self, new_game: bool):
        global game_ongoing
        # make new game but no ongoing game
        if new_game and not game_ongoing:
            game_ongoing = True
            self.overlay_menu['new'].setHidden(True)
        # make new game but there is ongoing game
        elif new_game and game_ongoing:
            game_ongoing = False
            pass
        # continue ongoing game
        else:
            game_ongoing = True
            pass

        if (gamemode == 'Bot') and bot_goes_first: bot_move()


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.addTab(Rules(), 'Rules and Info')
        self.addTab(Home(), 'Play')
        # add settings tab?
        # self.addTab(Settings(), 'Settings')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ultimate Tic-Tac-Toe")
        self.setGeometry(350, 100, *SCREEN_SIZE)
        self.setFixedSize(*SCREEN_SIZE)

        self.tabs = Tabs()
        self.tabs.setCurrentIndex(1)
        self.setCentralWidget(self.tabs)



if __name__=="__main__":
    SCREEN_SIZE = (800, 600)

    ult_tictactoe = QtWidgets.QApplication([])
    root = MainWindow()
    root.show()
    ult_tictactoe.exec()