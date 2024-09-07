
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as QtWidgets

from typing import Optional, Literal


x_turn: bool = True
current_board: Optional[tuple[int, int]] = None

COLOR: dict[str, str] = {'X': "color: rgb(255, 0, 0)",
                         'O': "color: rgb(0, 0, 255)",
                         'focus': "background-color: rgb(127, 255, 212)",
                         'non_focus': "background-color: rgb(60,60,60)"}

PLAYER_FONT: QFont = QFont()
PLAYER_FONT.setPointSize(30)

SMALL_WINNER_FONT: QFont = QFont()
SMALL_WINNER_FONT.setPointSize(100)

WINNER_FONT: QFont = QFont()
WINNER_FONT.setPointSize(300)


def play_turn(position: tuple[int, int], board: 'TicTacToe') -> None:
    global x_turn, current_board
    if current_board and current_board != board.position: return

    board.buttons[position[0]][position[1]].setText('X' if x_turn else 'O')
    board.buttons[position[0]][position[1]].setDisabled(True)
    x_turn = not x_turn

    if (temp := board.get_winner()):
        board.show_winner(temp)
    if (temp := game.get_winner()):
        game.show_winner(temp)
        return
    
    board.focus_board(False)
    if game.boards[position[0]][position[1]].overlay_label.isHidden():
        game.boards[position[0]][position[1]].focus_board()
        current_board = position
    else: current_board = None


class TicTacToe(QtWidgets.QWidget):
    def __init__(self, position: tuple[int, int], parent = None) -> None:
        super().__init__(parent)
        self.position = position

        self.setFixedSize(150, 150)

        self.vbox = QtWidgets.QVBoxLayout()
        self.hboxes = [QtWidgets.QHBoxLayout() for _ in range(3)]

        self.init_buttons()
        self.init_label_overlay()

        for hbox in self.hboxes:
            self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)
    

    def init_buttons(self) -> None:
        self.buttons: list[list[QtWidgets.QPushButton]] = [[] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i].append(QtWidgets.QPushButton(parent=self))
                self.buttons[i][j].setFont(PLAYER_FONT)
                self.buttons[i][j].setFixedSize(50, 50)
                
                self.hboxes[i].addWidget(self.buttons[i][j])
        self.buttons[0][0].pressed.connect(lambda: play_turn((0, 0), self))
        self.buttons[0][1].pressed.connect(lambda: play_turn((0, 1), self))
        self.buttons[0][2].pressed.connect(lambda: play_turn((0, 2), self))

        self.buttons[1][0].pressed.connect(lambda: play_turn((1, 0), self))
        self.buttons[1][1].pressed.connect(lambda: play_turn((1, 1), self))
        self.buttons[1][2].pressed.connect(lambda: play_turn((1, 2), self))

        self.buttons[2][0].pressed.connect(lambda: play_turn((2, 0), self))
        self.buttons[2][1].pressed.connect(lambda: play_turn((2, 1), self))
        self.buttons[2][2].pressed.connect(lambda: play_turn((2, 2), self))

    def init_label_overlay(self) -> None:
        self.overlay_label = QtWidgets.QLabel('', parent=self)
        self.overlay_label.setFont(SMALL_WINNER_FONT)
        self.overlay_label.setFixedSize(140, 140)
        self.overlay_label.setHidden(True)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.move(10, 10)


    def reset(self) -> None:
        global x_turn
        x_turn = True
        self.overlay_label.setText('')
        self.overlay_label.setHidden(True)
        for row in self.buttons:
            for button in row:
                button.setText('')
                button.setEnabled(True)

    def get_winner(self) -> Literal['X', 'O', 'Tie', '']:
        empty_square: bool = False
        main_diag = []
        sub_diag = []
        for i in range(3):
            row, col = '', ''
            for j in range(3):
                row += self.buttons[i][j].text()
                col += self.buttons[j][i].text()
            main_diag.append(self.buttons[i][i].text())
            sub_diag.append(self.buttons[2 - i][i].text())
            if (len(set(row)) == 1) and (len(row) == 3): return row[0]
            if (len(set(col)) == 1) and (len(col) == 3): return col[0]
            if len(row) != 3 or len(col) != 3: empty_square = True
        
        if len(set(main_diag)) == 1: return main_diag[0]
        if len(set(sub_diag)) == 1: return sub_diag[0]

        return '' if empty_square else 'Tie'

    def show_winner(self, winner: Literal['X', 'O', 'Tie']) -> None:
        color = "background-color: rgba(255, 255, 255, 15)"
        if winner == 'X': color += f"; {COLOR['X']}"
        elif winner == 'O': color += f"; {COLOR['O']}"
        else: winner = ''
        self.overlay_label.setStyleSheet(color)
        self.overlay_label.setText(winner)
        self.overlay_label.setHidden(False)

    def focus_board(self, focus: bool = True) -> None:
        for row in self.buttons:
            for button in row:
                if focus: color = COLOR['focus']
                else: color = COLOR['non_focus']
                if button.text() == 'X': color += f"; {COLOR['X']}"
                else: color += f"; {COLOR['O']}"
                button.setStyleSheet(color)

class UltimateTicTacToe(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(480, 480)

        self.vbox = QtWidgets.QVBoxLayout()
        self.hboxes = [QtWidgets.QHBoxLayout() for _ in range(3)]

        self.init_boards()
        self.init_overlay()

        for hbox in self.hboxes:
            self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)

    def init_boards(self) -> None:
        self.boards: list[list[TicTacToe]] = [[] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.boards[i].append(TicTacToe((i, j), self))
                self.hboxes[i].addWidget(self.boards[i][j])

    def init_overlay(self) -> None:
        self.overlay_label = QtWidgets.QLabel('', self)
        self.overlay_label.setFont(WINNER_FONT)
        self.overlay_label.setFixedSize(450, 450)
        self.overlay_label.setHidden(True)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.move(20, 20)

    def show_winner(self, winner: Literal['X', 'O', 'Tie']) -> None:
        color = "background-color: rgba(255, 255, 255, 50)"
        if winner == 'X': color += f"; {COLOR['X']}"
        elif winner == 'O': color += f"; {COLOR['O']}"
        else: winner = ''
        self.overlay_label.setStyleSheet(color)
        self.overlay_label.setText(winner)
        self.overlay_label.setHidden(False)

    def get_winner(self) -> Literal['X', 'O', 'Tie', '']:
        empty_square: bool = False
        main_diag = []
        sub_diag = []
        for i in range(3):
            row, col = '', ''
            for j in range(3):
                row += self.boards[i][j].overlay_label.text()
                col += self.boards[j][i].overlay_label.text()
            main_diag.append(self.boards[i][i].overlay_label.text())
            sub_diag.append(self.boards[2 - i][i].overlay_label.text())
            if (len(set(row)) == 1) and (len(row) == 3): return row[0]
            if (len(set(col)) == 1) and (len(col) == 3): return col[0]
            if len(row) != 3 or len(col) != 3: empty_square = True
        
        if len(set(main_diag)) == 1: return main_diag[0]
        if len(set(sub_diag)) == 1: return sub_diag[0]

        return '' if empty_square else 'Tie'


class Rules(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel(r"¯\_(ツ)_/¯", parent=self)

class Home(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()

        global game
        game = UltimateTicTacToe()

        self.init_buttons()

        self.vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(game)

        self.setLayout(self.vbox)

    def init_buttons(self) -> None:
        self.hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.reset_button = QtWidgets.QPushButton('New Game', parent=self)
        self.reset_button.setFixedSize(80, 30)
        self.reset_button.clicked.connect(self.restart)
        self.hbox.addWidget(self.reset_button)

    def restart(self):
        global current_board, x_turn
        x_turn = True

        game.overlay_label.setHidden(True)

        if current_board:
            game.boards[current_board[0]][current_board[1]].focus_board(False)
            current_board = None

        for row in game.boards:
            for board in row:
                board.reset()


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.addTab(Rules(), 'Rules and Info')
        self.addTab(Home(), 'Play')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ultimate Tic-Tac-Toe")
        self.setGeometry(350, 100, 800, 600)
        self.tabs = Tabs()
        self.tabs.setCurrentIndex(1)
        self.setCentralWidget(self.tabs)



def main():
    ult_tictactoe = QtWidgets.QApplication([])
    root = MainWindow()
    root.show()
    ult_tictactoe.exec()

if __name__=="__main__":
    main()