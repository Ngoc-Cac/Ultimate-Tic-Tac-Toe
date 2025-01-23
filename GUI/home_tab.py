import os.path as osp

from PyQt6.QtCore import (
    Qt,
    QSize,
    pyqtSignal
)
from PyQt6.QtGui import (
    QFont,
    QIcon
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QStyle,
    QTabBar,
    QVBoxLayout,
    QWidget
)

from GUI.menus import (
    InGameMenu,
    NewGameMenu,
    SettingsMenu
)
from GUI.tictactoe_board import UltimateTicTacToe


from typing import Literal


INFO_FONT: QFont = QFont()
INFO_FONT.setPointSize(16)


class Home(QWidget):
    gamemode_changed = pyqtSignal(str)
    gametype_changed = pyqtSignal(str)
    bot_algo_changed = pyqtSignal(str)
    first_turn_changed = pyqtSignal(str) # Bot or Human

    game_about_to_start = pyqtSignal(bool)
    restart_signal = pyqtSignal()
    undo_signal = pyqtSignal()

    def __init__(self, game: UltimateTicTacToe, screen_size: tuple[int, int]):
        super().__init__()
        self.init_gamezone(game)
        self.init_menus(screen_size)

    def init_menus(self, screen_size: tuple[int, int]):
        bg_color = "background-color: rgba(0, 0, 0, 170)"
        self.overlay_menu: dict[Literal['new', 'in-game'], QFrame] = {}
        self.overlay_menu['new'] = NewGameMenu(self)
        self.overlay_menu['new'].play_button.clicked.connect(lambda: self.start_game(True))
        self.overlay_menu['new'].gametype_box.currentTextChanged.connect(self.change_gametype)
        self.overlay_menu['new'].mode_box.currentTextChanged.connect(self.change_gamemode)
        self.overlay_menu['new'].choose_turn_butt.clicked.connect(self.change_turn)
        self.overlay_menu['new'].choose_algo_box.currentTextChanged.connect(self.change_bot_algo)

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

        self.overlay_menu['new'].setFixedSize(*screen_size)
        self.overlay_menu['in-game'].setFixedSize(*screen_size)
        self.overlay_menu['settings'].setFixedSize(*screen_size)

    def init_gamezone(self, game: UltimateTicTacToe) -> None:
        hamburg_ico = QIcon(osp.join('.', 'resource', 'hamburg.png'))
        settings_ico = QIcon(osp.join('.', 'resource', 'cogwheel.png'))
        tabbar = QTabBar(self)
        tabbar.setDrawBase(False)
        tabbar.setStyleSheet("""QTabBar::tab {background-color: transparent;}""")
        tabbar.setFixedSize(118, 50)
        tabbar.setIconSize(QSize(30, 30))

        tabbar.addTab(hamburg_ico, None)
        tabbar.addTab(settings_ico, None)
        tabbar.tabBarClicked.connect(self.ingame_menu_popup)
        

        restart_button = QPushButton('Restart')
        restart_button.setFixedSize(70, 30)
        restart_button.clicked.connect(lambda: self.restart_signal.emit())

        undo_button = QPushButton('Undo')
        undo_button.setFixedSize(60, 30)
        undo_button.clicked.connect(lambda: self.undo_signal.emit())


        hbox = QHBoxLayout()
        hbox.addWidget(undo_button)
        hbox.addWidget(restart_button)
        hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(game)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(vbox)


    def change_gamemode(self, text: Literal['Human', 'Bot']):
        self.overlay_menu['new'].choose_turn_butt.setHidden(text == 'Human')
        self.overlay_menu['new'].choose_algo_box.setHidden(text == 'Human')
        self.overlay_menu['new'].algo_label.setHidden(text == 'Human')
        self.gamemode_changed.emit(text)
    
    def change_gametype(self, text: Literal['Normal', 'Ultimate']):
        self.gametype_changed.emit(text)

    def change_turn(self):
        prev_subject = self.overlay_menu['new'].choose_turn_butt.text().split(' ')[0]
        subject = 'Bot' if prev_subject == 'Human' else 'Human'
        self.overlay_menu['new'].choose_turn_butt.setText(subject + ' goes first!')
        self.first_turn_changed.emit(subject)

    def change_bot_algo(self, text: Literal['Minimax', 'Monte Carlo Tree Search']):
        self.bot_algo_changed.emit(text)

    def ingame_menu_popup(self, tab_index: int):
        if tab_index == 0:
            self.overlay_menu['in-game'].setHidden(False)
        elif tab_index == 1:
            self.overlay_menu['settings'].setHidden(False)


    def start_game(self, new_game: bool):
        self.game_about_to_start.emit(new_game)

        if new_game:
            hidden_state = self.overlay_menu['new'].isHidden()
            self.overlay_menu['new'].setHidden(not hidden_state)
        self.overlay_menu['in-game'].setHidden(True)
        self.overlay_menu['settings'].setHidden(True)