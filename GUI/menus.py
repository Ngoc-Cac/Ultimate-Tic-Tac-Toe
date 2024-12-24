from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as QtWidgets

from typing import Callable

INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)

TRANSPARENT_BG: str = "background-color: transparent"

class NewGameMenu(QtWidgets.QFrame):
    def __init__(self, start_game_func: Callable[[bool], None],
                 change_gametype_func: Callable[[], None],
                 change_gamemode_func: Callable[[], None],
                 change_turn_func: Callable[[], None],
                 parent = None) -> None:
        super().__init__(parent)
        # new game menu
        vbox = QtWidgets.QVBoxLayout()

        ## game type choosing zone
        gametype_hbox = self.init_gametype_zone(change_gametype_func)
        
        ## mode choosing zone
        mode_hbox = self.init_gamemode_zone(change_gamemode_func, change_turn_func)

        ## play button zone
        play_button = QtWidgets.QPushButton('Play!')
        play_button.clicked.connect(lambda: start_game_func(True))
        play_button.setStyleSheet(TRANSPARENT_BG)
        play_button.setFont(INFO_FONT)
        play_button.setFixedSize(100, 50)

        vbox.addLayout(gametype_hbox)
        vbox.addLayout(mode_hbox)
        vbox.addWidget(play_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)

    def init_gametype_zone(self, change_gametype_func: Callable[[], None]):
        gametype_box = QtWidgets.QComboBox()
        gametype_box.addItems(['Normal', 'Ultimate'])
        gametype_box.setCurrentIndex(1)
        gametype_box.setStyleSheet(TRANSPARENT_BG)
        gametype_box.setFont(INFO_FONT)
        gametype_box.setFixedSize(115, 50)
        gametype_box.currentTextChanged.connect(change_gametype_func)

        decorative_label = QtWidgets.QLabel('Game Type:')
        decorative_label.setStyleSheet(TRANSPARENT_BG)
        decorative_label.setFont(INFO_FONT)
        decorative_label.setFixedSize(110, 30)
        decorative_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        gametype_hbox = QtWidgets.QHBoxLayout()
        gametype_hbox.addWidget(decorative_label)
        gametype_hbox.addWidget(gametype_box)
        gametype_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return gametype_hbox
    
    def init_gamemode_zone(self, change_gamemode_func: Callable[[], None],
                           change_turn_func: Callable[[], None]):
        mode_box = QtWidgets.QComboBox()
        mode_box.addItems(['Human', 'Bot'])
        mode_box.setStyleSheet(TRANSPARENT_BG)
        mode_box.setFont(INFO_FONT)
        mode_box.setFixedSize(115, 50)
        mode_box.currentTextChanged.connect(change_gamemode_func)

        
        self.choose_turn_butt = QtWidgets.QPushButton('Bot goes first!')
        self.choose_turn_butt.setFont(INFO_FONT)
        self.choose_turn_butt.setHidden(True)
        self.choose_turn_butt.setFixedSize(200, 50)
        self.choose_turn_butt.setStyleSheet(TRANSPARENT_BG)
        self.choose_turn_butt.clicked.connect(change_turn_func)

        decorative_label = QtWidgets.QLabel('Mode:')
        decorative_label.setStyleSheet(TRANSPARENT_BG)
        decorative_label.setFont(INFO_FONT)
        decorative_label.setFixedSize(110, 30)
        decorative_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        mode_hbox = QtWidgets.QHBoxLayout()
        mode_hbox.addWidget(decorative_label)
        mode_hbox.addWidget(mode_box)
        mode_hbox.addWidget(self.choose_turn_butt)
        mode_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return mode_hbox
    
class InGameMenu(QtWidgets.QFrame):
    def __init__(self, continue_game_func: Callable[[], None],
                 new_game_func: Callable[[], None],
                 parent = None):
        super().__init__(parent)

        continue_butt = QtWidgets.QPushButton('Continue Game')
        continue_butt.clicked.connect(continue_game_func)
        continue_butt.setFont(INFO_FONT)
        continue_butt.setFixedSize(180, 50)
        continue_butt.setStyleSheet(TRANSPARENT_BG)

        new_game_butt = QtWidgets.QPushButton('New Game')
        new_game_butt.clicked.connect(new_game_func)
        new_game_butt.setFont(INFO_FONT)
        new_game_butt.setFixedSize(180, 50)
        new_game_butt.setStyleSheet(TRANSPARENT_BG)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(continue_butt)
        vbox.addWidget(new_game_butt)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)