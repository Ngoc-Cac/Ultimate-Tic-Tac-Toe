from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QVBoxLayout
)


INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)

TRANSPARENT_BG: str = "background-color: transparent"

class NewGameMenu(QFrame):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        # new game menu
        vbox = QVBoxLayout()

        ## game type choosing zone
        gametype_hbox = self.init_gametype_zone()
        
        ## mode choosing zone
        mode_hbox = self.init_gamemode_zone()
        algo_hbox = self.init_algo_zone()

        ## play button zone
        self.play_button = QPushButton('Play!')
        self.play_button.setStyleSheet(TRANSPARENT_BG)
        self.play_button.setFont(INFO_FONT)
        self.play_button.setFixedSize(100, 50)

        vbox.addLayout(gametype_hbox)
        vbox.addLayout(mode_hbox)
        vbox.addLayout(algo_hbox)
        vbox.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)

    def init_gametype_zone(self):
        self.gametype_box = QComboBox()
        self.gametype_box.addItems(['Normal', 'Ultimate'])
        self.gametype_box.setCurrentIndex(1)
        self.gametype_box.setStyleSheet(TRANSPARENT_BG)
        self.gametype_box.setFont(INFO_FONT)
        self.gametype_box.setFixedSize(115, 50)

        decorative_label = QLabel('Game Type:')
        decorative_label.setStyleSheet(TRANSPARENT_BG)
        decorative_label.setFont(INFO_FONT)
        decorative_label.setFixedSize(110, 30)
        decorative_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        gametype_hbox = QHBoxLayout()
        gametype_hbox.addWidget(decorative_label)
        gametype_hbox.addWidget(self.gametype_box)
        gametype_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return gametype_hbox
    
    def init_gamemode_zone(self):
        self.mode_box = QComboBox()
        self.mode_box.addItems(['Human', 'Bot'])
        self.mode_box.setStyleSheet(TRANSPARENT_BG)
        self.mode_box.setFont(INFO_FONT)
        self.mode_box.setFixedSize(115, 50)

        
        self.choose_turn_butt = QPushButton('Bot goes first!')
        self.choose_turn_butt.setFont(INFO_FONT)
        self.choose_turn_butt.setHidden(True)
        self.choose_turn_butt.setFixedSize(200, 50)
        self.choose_turn_butt.setStyleSheet(TRANSPARENT_BG)


        decorative_label = QLabel('Mode:')
        decorative_label.setStyleSheet(TRANSPARENT_BG)
        decorative_label.setFont(INFO_FONT)
        decorative_label.setFixedSize(110, 30)
        decorative_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        mode_hbox = QHBoxLayout()
        mode_hbox.addWidget(decorative_label)
        mode_hbox.addWidget(self.mode_box)
        mode_hbox.addWidget(self.choose_turn_butt)
        mode_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return mode_hbox
    
    def init_algo_zone(self):
        self.choose_algo_box = QComboBox()
        self.choose_algo_box.addItems(['Minimax', 'Monte Carlo Tree Search'])
        self.choose_algo_box.setCurrentIndex(1)
        self.choose_algo_box.setStyleSheet(TRANSPARENT_BG)
        self.choose_algo_box.setFont(INFO_FONT)
        self.choose_algo_box.setFixedSize(260, 50)
        self.choose_algo_box.setHidden(True)

        self.algo_label = QLabel('Algorithm:')
        self.algo_label.setStyleSheet(TRANSPARENT_BG)
        self.algo_label.setFont(INFO_FONT)
        self.algo_label.setFixedSize(110, 30)
        self.algo_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.algo_label.setHidden(True)

        algo_hbox = QHBoxLayout()
        algo_hbox.addWidget(self.algo_label)
        algo_hbox.addWidget(self.choose_algo_box)
        algo_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return algo_hbox
    
class InGameMenu(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.continue_butt = QPushButton('Continue Game')
        self.continue_butt.setFont(INFO_FONT)
        self.continue_butt.setFixedSize(180, 50)
        self.continue_butt.setStyleSheet(TRANSPARENT_BG)

        self.new_game_butt = QPushButton('New Game')
        self.new_game_butt.setFont(INFO_FONT)
        self.new_game_butt.setFixedSize(180, 50)
        self.new_game_butt.setStyleSheet(TRANSPARENT_BG)

        vbox = QVBoxLayout()
        vbox.addWidget(self.continue_butt)
        vbox.addWidget(self.new_game_butt)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)

class SettingsMenu(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.continue_butt = QPushButton('Continue Game')
        self.continue_butt.setFont(INFO_FONT)
        self.continue_butt.setFixedSize(180, 50)
        self.continue_butt.setStyleSheet(TRANSPARENT_BG)

        algo_zone = self.init_algo_choice()
        
        vbox = QVBoxLayout()
        vbox.addLayout(algo_zone)
        vbox.addWidget(self.continue_butt, alignment=Qt.AlignmentFlag.AlignHCenter)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)

    def init_algo_choice(self):
        self.algo_box = QComboBox()
        self.algo_box.addItems(['Minimax', 'Monte Carlo Tree Search'])
        self.algo_box.setCurrentIndex(1)
        self.algo_box.setStyleSheet(TRANSPARENT_BG)
        self.algo_box.setFont(INFO_FONT)
        self.algo_box.setFixedSize(260, 50)

        info_label = QLabel('Algorithm:')
        info_label.setStyleSheet(TRANSPARENT_BG)
        info_label.setFont(INFO_FONT)
        info_label.setFixedSize(110, 30)
        info_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        hbox = QHBoxLayout()
        hbox.addWidget(info_label)
        hbox.addWidget(self.algo_box)
        hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        return hbox