
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as QtWidgets

from tictactoe import TicTacToe, UltimateTicTacToe

from typing import Optional, Literal


x_turn: bool = True
current_board: Optional[tuple[int, int]] = None
prev_states: list[tuple[tuple[int, int], 'TicTacToe']] = []


def restart():
    global current_board, x_turn
    x_turn = True

    game.overlay_label.setHidden(True)

    if current_board:
        game.boards[current_board[0]][current_board[1]].focus_board(False)
        current_board = None

    for row in game.boards:
        for board in row:
            board.reset()

def undo_move():
    if (not len(prev_states)) or game.get_winner(): return
    global x_turn, current_board
    
    prev_state = prev_states.pop()
    game.boards[prev_state[0][0]][prev_state[0][1]].focus_board(False)
    
    if prev_state[1].get_winner(): prev_state[1].reset_winner()
    prev_state[1].buttons[prev_state[0][0]][prev_state[0][1]].setText('')
    prev_state[1].buttons[prev_state[0][0]][prev_state[0][1]].setDisabled(False)

    if len(prev_states):
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
        game.boards[position[0]][position[1]].focus_board()
        current_board = position
    else: current_board = None


class Rules(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel(r"¯\_(ツ)_/¯", parent=self)

class Home(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_gamezone()

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


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.addTab(Rules(), 'Rules and Info')
        self.addTab(Home(), 'Play')

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