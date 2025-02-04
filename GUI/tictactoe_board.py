from PyQt6.QtCore import Qt
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

import logging
logger = logging.getLogger(__name__)
"""
Code for building the Tic-Tac-Toe UI.
"""


COLOR: dict[str, str] = {'X': "color: rgb(255, 49, 49)",
                         'O': "color: rgb(0, 131, 255)",
                         'T': "color: rgb(255, 255, 255)",
                         'focus': "background-color: rgb(186, 255, 201)"}

def _get_winner(tictactoe_board: list[list[Literal['X', 'O', '']]]):
    """
    Get the winner from a Tic-Tac-Toe board.

    ## Parameters:
    `tictactoe_board`: a 3x3 grid containing characters 'X', 'O' or ''.

    ## Return
    'X', 'O' if either of them won the game, 'T' if the game ended in a tie,\
        '' if the game is not over.
    """
    empty_square: bool = False
    main_diag = []
    sub_diag = []
    for i, lis in enumerate(tictactoe_board):
        row, col = '', ''
        for j, val in enumerate(lis):
            row += val
            col += tictactoe_board[j][i]
        main_diag.append(lis[i])
        sub_diag.append(tictactoe_board[2 - i][i])
        if (len(row) == 3) and (len(set(row)) == 1): return row[0]
        if (len(col) == 3) and (len(set(col)) == 1): return col[0]
        if (len(row) != 3) or (len(col) != 3): empty_square = True
    
    if len(set(main_diag)) == 1: return main_diag[0]
    if len(set(sub_diag)) == 1: return sub_diag[0]

    return '' if empty_square else 'T'


class TicTacToe(QWidget):
    """
    A Tic-Tac-Toe board. This is a widget containing a 3x3 grid of\
        clickable buttons.
    This widget is used for a larger container widget. The buttons\
        in this widget is connected automatically to a given function\
        that formats the board accordingly.
    """
    def __init__(self, position: tuple[int, int],
                 format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None],
                 parent = None) -> None:
        super().__init__(parent)
        self.position = position

        self.setFixedSize(150, 150)

        self.vbox = QVBoxLayout()
        self.hboxes = [QHBoxLayout() for _ in range(3)]

        self._init_buttons(format_board_func)
        self._init_overlay()

        for hbox in self.hboxes:
            self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)
    

    def _init_buttons(self, format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None]) -> None:
        self.buttons: list[list[QPushButton]] = [[] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i].append(QPushButton(parent=self))
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

    def _init_overlay(self) -> None:
        self.overlay_label = QLabel('', parent=self)
        self.overlay_label.setFixedSize(140, 140)
        self.overlay_label.setHidden(True)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.move(10, 10)


    def reset(self) -> None:
        """Reset the board to the default state"""
        self.overlay_label.setText('')
        self.overlay_label.setHidden(True)
        for row in self.buttons:
            for button in row:
                button.setText('')
                button.setEnabled(True)

    def get_winner(self) -> Literal['X', 'O', 'T', '']:
        """
        Get the winner from the current board.

        # Return
        Return the character that won this board, 'T' if it's\
            a tie or '' if this board is still playable.
        """
        return _get_winner([[button.text() for button in row] for row in self.buttons])

    def show_winner(self, winner: Literal['X', 'O', 'T']) -> None:
        """
        Show the winner on this board's overlay label.
        The board will not be playable anymore once shown.
        """
        color = COLOR[winner]
        self.overlay_label.setText(winner)
        self.overlay_label.setStyleSheet(color)
        self.overlay_label.setHidden(False)

    def reset_winner(self) -> None:
        """Hide the overlay label, making this board playable"""
        self.overlay_label.setHidden(True)

    def focus_board(self, focus: bool = True) -> None:
        """Apply the focus effect on this board if `focus=True`"""
        for row in self.buttons:
            for button in row:
                char = button.text()
                color = COLOR['focus'] if focus else ''
                color += "; " + COLOR[char if char else 'T']
                button.setStyleSheet(color)

    def get_state(self) -> list[list[Literal['X', 'O', ' ']]]:
        """Get the 3x3 grid of string literals for this board"""
        return [[button.text() if button.text() else EMPTY_CHAR for button in row]
                for row in self.buttons]

class UltimateTicTacToe(QWidget):
    """
    The main Ultimate Tic-Tac-Toe board in the window.
    This widget contains a 3x3 grid of TicTacToe widgets. 
    """
    def __init__(self, format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None]):
        super().__init__()

        self.setFixedSize(480, 480)

        self.vbox = QVBoxLayout()
        self.hboxes = [QHBoxLayout() for _ in range(3)]

        self._init_boards(format_board_func)
        self._init_overlay()

        for hbox in self.hboxes:
            self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)

    def _init_boards(self, format_board_func: Callable[[tuple[int, int], 'TicTacToe'], None]) -> None:
        self.boards: list[list[TicTacToe]] = [[] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.boards[i].append(TicTacToe((i, j), format_board_func, self))
                self.hboxes[i].addWidget(self.boards[i][j])

    def _init_overlay(self) -> None:
        self.overlay_label = QLabel('', self)
        self.overlay_label.setFixedSize(450, 450)
        self.overlay_label.setHidden(True)
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.move(20, 20)


    def show_winner(self, winner: Literal['X', 'O', 'T']) -> None:
        """
        Show the winner on the board's overlay label.
        The board will not be playable anymore once shown.
        """
        color = COLOR[winner]
        self.overlay_label.setText(winner)
        self.overlay_label.setStyleSheet(color)
        self.overlay_label.setHidden(False)

    def block_clicks(self, block: bool) -> None:
        """Block any clicks on the buttons of the TicTacToe widget"""
        self.overlay_label.setText('')
        self.overlay_label.setStyleSheet("background-color: rgba(255, 255, 255, 10)" if block else '')
        self.overlay_label.setHidden(not block)

    def switch_mode(self, mode: Literal['Ultimate', 'Normal']) -> None:
        """
        Switch between Ultimate and Normal mode.\
            Normal mode disables all children TicTacToe widgets except the\
            center one.
        """
        for i, row in enumerate(self.boards):
            for j, board in enumerate(row):
                if i == j == 1: continue
                board.overlay_label.setText('')
                board.overlay_label.setHidden(mode != 'Normal')


    def get_winner(self, mode: Literal['Ultimate', 'Normal']) -> Literal['X', 'O', 'T', '']:
        """Get the winner from the current board.

        # Return
        Return the character that won this board, 'T' if it's\
            a tie or '' if this board is still playable."""
        if mode == 'Ultimate':
            tictactoe_board = [[board.overlay_label.text() for board in row] for row in self.boards]
        else:
            tictactoe_board = [[button.text() for button in row] for row in self.boards[1][1].buttons]
        return _get_winner(tictactoe_board)
    
    def get_state(self) -> list[list[Literal['X', 'O', 'T', ' ']]]:
        """Get the 3x3 grid of string literals for this board"""
        return [[txt if (txt := board.overlay_label.text()) else EMPTY_CHAR
                 for board in row] for row in self.boards]