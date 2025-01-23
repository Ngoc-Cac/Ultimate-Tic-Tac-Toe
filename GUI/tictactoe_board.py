from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from bot.gamestate import EMPTY_CHAR

from typing import (
    Literal,
    Callable
)


COLOR: dict[str, str] = {'X': "color: rgb(255, 0, 0)",
                         'O': "color: rgb(0, 0, 255)",
                         'T': "color: rgb(255, 255, 255)",
                         'focus': "background-color: rgb(127, 255, 212)",
                         'non_focus': "background-color: rgb(60,60,60)"}

PLAYER_FONT: QFont = QFont()
PLAYER_FONT.setPointSize(30)

SMALL_WINNER_FONT: QFont = QFont()
SMALL_WINNER_FONT.setPointSize(100)

WINNER_FONT: QFont = QFont()
WINNER_FONT.setPointSize(300)


class TicTacToe(QWidget):
    def __init__(self, position: tuple[int, int],
                 format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None],
                 parent = None) -> None:
        super().__init__(parent)
        self.position = position

        self.setFixedSize(150, 150)

        self.vbox = QVBoxLayout()
        self.hboxes = [QHBoxLayout() for _ in range(3)]

        self.init_buttons(format_board_func)
        self.init_overlay()

        for hbox in self.hboxes:
            self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)
    

    def init_buttons(self, format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None]) -> None:
        self.buttons: list[list[QPushButton]] = [[] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i].append(QPushButton(parent=self))
                self.buttons[i][j].setFont(PLAYER_FONT)
                self.buttons[i][j].setFixedSize(50, 50)
                
                self.hboxes[i].addWidget(self.buttons[i][j])
        self.buttons[0][0].pressed.connect(lambda: format_board_func((0, 0), self))
        self.buttons[0][1].pressed.connect(lambda: format_board_func((0, 1), self))
        self.buttons[0][2].pressed.connect(lambda: format_board_func((0, 2), self))

        self.buttons[1][0].pressed.connect(lambda: format_board_func((1, 0), self))
        self.buttons[1][1].pressed.connect(lambda: format_board_func((1, 1), self))
        self.buttons[1][2].pressed.connect(lambda: format_board_func((1, 2), self))

        self.buttons[2][0].pressed.connect(lambda: format_board_func((2, 0), self))
        self.buttons[2][1].pressed.connect(lambda: format_board_func((2, 1), self))
        self.buttons[2][2].pressed.connect(lambda: format_board_func((2, 2), self))

    def init_overlay(self) -> None:
        self.overlay_label = QLabel('', parent=self)
        self.overlay_label.setFont(SMALL_WINNER_FONT)
        self.overlay_label.setFixedSize(140, 140)
        self.overlay_label.setHidden(True)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet("background-color: rgba(255, 255, 255, 15)")
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

    def get_winner(self) -> Literal['X', 'O', 'T', '']:
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
            if (len(row) == 3) and (len(set(row)) == 1): return row[0]
            if (len(col) == 3) and (len(set(col)) == 1): return col[0]
            if (len(row) != 3) or (len(col) != 3): empty_square = True
        
        if len(set(main_diag)) == 1: return main_diag[0]
        if len(set(sub_diag)) == 1: return sub_diag[0]

        return '' if empty_square else 'T'

    def show_winner(self, winner: Literal['X', 'O', 'T']) -> None:
        color = "background-color: rgba(255, 255, 255, 15)"
        color += "; " + COLOR[winner]
        self.overlay_label.setText(winner)
        self.overlay_label.setStyleSheet(color)
        self.overlay_label.setHidden(False)

    def reset_winner(self) -> None:
        self.overlay_label.setHidden(True)

    def focus_board(self, focus: bool = True) -> None:
        for row in self.buttons:
            for button in row:
                char = button.text()
                color = COLOR['focus' if focus else 'non_focus']
                color += "; " + COLOR[char if char else 'T']
                button.setStyleSheet(color)

    def get_state(self) -> list[list[Literal['X', 'O', ' ']]]:
        return [[button.text() if button.text() else EMPTY_CHAR for button in row]
                for row in self.buttons]

class UltimateTicTacToe(QWidget):
    def __init__(self, format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None]):
        super().__init__()

        self.setFixedSize(480, 480)

        self.vbox = QVBoxLayout()
        self.hboxes = [QHBoxLayout() for _ in range(3)]

        self.init_boards(format_board_func)
        self.init_overlay()

        for hbox in self.hboxes:
            self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)

    def init_boards(self, format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None]) -> None:
        self.boards: list[list[TicTacToe]] = [[] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.boards[i].append(TicTacToe((i, j), format_board_func, self))
                self.hboxes[i].addWidget(self.boards[i][j])

    def init_overlay(self) -> None:
        self.overlay_label = QLabel('', self)
        self.overlay_label.setFont(WINNER_FONT)
        self.overlay_label.setFixedSize(450, 450)
        self.overlay_label.setHidden(True)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet("background-color: rgba(255, 255, 255, 50)")
        self.overlay_label.move(20, 20)

    def show_winner(self, winner: Literal['X', 'O', 'T']) -> None:
        color = "background-color: rgba(255, 255, 255, 50)"
        color += "; " + COLOR[winner]
        self.overlay_label.setText(winner)
        self.overlay_label.setStyleSheet(color)
        self.overlay_label.setHidden(False)

    def block_clicks(self, block: bool) -> None:
        self.overlay_label.setStyleSheet(f"background-color: rgba(255, 255, 255, {0 if block else 50})")
        self.overlay_label.setHidden(not block)

    def get_winner(self) -> Literal['X', 'O', 'T', '']:
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

        return '' if empty_square else 'T'
    
    def get_state(self) -> list[list[Literal['X', 'O', ' ']]]:
        return [[txt if (txt := board.overlay_label.text()) else EMPTY_CHAR
                 for board in row] for row in self.boards]