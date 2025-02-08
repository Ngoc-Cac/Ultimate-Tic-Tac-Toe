import os.path as osp

from PyQt6.QtCore import (
    Qt,
    pyqtSignal
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QTabBar,
    QVBoxLayout,
    QWidget
)

from GUI import _ROOT_DIR
from GUI.menus import (
    InGameMenu,
    NewGameMenu,
    SettingsMenu
)
from GUI.tictactoe_board import UltimateTicTacToe


from typing import Literal
"""
Code for building Home tab UI
"""


class Home(QWidget):
    theme_changed = pyqtSignal(str) # dark or light

    gamemode_changed = pyqtSignal(str) # Human or Bot
    gametype_changed = pyqtSignal(str) # Normal or Ultimate
    bot_algo_changed = pyqtSignal(str) # Minimax or Monte Carlo Tree Search
    first_turn_changed = pyqtSignal(str) # Bot or Human

    game_about_to_start = pyqtSignal(bool)
    restart_signal = pyqtSignal()
    undo_signal = pyqtSignal()

    def __init__(self, game: UltimateTicTacToe, screen_size: tuple[int, int]):
        super().__init__()
        self._init_icons()

        self.tabbar = QTabBar(self)
        self.tabbar.setFixedSize(118, 50)

        self.tabbar.addTab(self.icons['hamburger']['Dark'], None)
        self.tabbar.addTab(self.icons['cogwheel']['Dark'], None)
        self.tabbar.tabBarClicked.connect(self._ingame_menu_popup)

        hbox = self._init_buttons()
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(game)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)

        # menus must be init last for correct z-ordering
        self._init_menus(screen_size)

    def _init_icons(self):
        self.icons = {}
        self.icons['hamburger'] = {
            'Light': QIcon(osp.join(_ROOT_DIR, 'resource', 'icons', 'hamburg_black.png')),
            'Dark': QIcon(osp.join(_ROOT_DIR, 'resource', 'icons', 'hamburg_white.png'))
        }
        self.icons['cogwheel'] = {
            'Light': QIcon(osp.join(_ROOT_DIR, 'resource', 'icons', 'cogwheel_black.png')),
            'Dark': QIcon(osp.join(_ROOT_DIR, 'resource', 'icons', 'cogwheel_white.png'))
        }

    def _init_menus(self, screen_size: tuple[int, int]):
        self.overlay_menu: dict[Literal['new', 'in-game', 'settings'], QFrame] = {}
        self.overlay_menu['new'] = NewGameMenu(self)
        self.overlay_menu['new'].play_button.clicked.connect(lambda: self._start_game(True))
        self.overlay_menu['new'].gametype_box.currentTextChanged.connect(self._change_gametype)
        self.overlay_menu['new'].mode_box.currentTextChanged.connect(self._change_gamemode)
        self.overlay_menu['new'].choose_turn_butt.clicked.connect(self._change_turn)
        self.overlay_menu['new'].algo_box.currentTextChanged\
                                .connect(lambda txt: self._change_bot_algo(txt, 'new'))

        self.overlay_menu['in-game'] = InGameMenu(self)
        self.overlay_menu['in-game'].continue_butt.clicked.connect(lambda: self._start_game(False))
        self.overlay_menu['in-game'].new_game_butt.clicked.connect(lambda: self._start_game(True))

        self.overlay_menu['settings'] = SettingsMenu(self)
        self.overlay_menu['settings'].continue_butt.clicked.connect(lambda: self._start_game(False))
        self.overlay_menu['settings'].algo_box.currentTextChanged\
                                     .connect(lambda txt: self._change_bot_algo(txt, 'settings'))
        self.overlay_menu['settings'].theme_butt.clicked.connect(self._change_theme)


        self.overlay_menu['in-game'].setHidden(True)
        self.overlay_menu['settings'].setHidden(True)
        self.overlay_menu['new'].setFixedSize(*screen_size)
        self.overlay_menu['in-game'].setFixedSize(*screen_size)
        self.overlay_menu['settings'].setFixedSize(*screen_size)

    def _init_buttons(self) -> None:
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
        return hbox


    def _change_theme(self):
        prev_theme = self.overlay_menu['settings'].theme_butt.text()
        new_theme = 'Light' if prev_theme == 'Dark' else 'Dark'

        self.overlay_menu['settings'].theme_butt.setText(new_theme)
        self.tabbar.setTabIcon(0, self.icons['hamburger'][new_theme])
        self.tabbar.setTabIcon(1, self.icons['cogwheel'][new_theme])

        self.theme_changed.emit(new_theme.lower())

    def _change_gamemode(self, text: Literal['Human', 'Bot']):
        self.overlay_menu['new'].choose_turn_butt.setHidden(text == 'Human')
        self.overlay_menu['new'].algo_box.setHidden(text == 'Human')
        self.overlay_menu['new'].algo_label.setHidden(text == 'Human')
        self.gamemode_changed.emit(text)
    
    def _change_gametype(self, text: Literal['Normal', 'Ultimate']):
        self.gametype_changed.emit(text)

    def _change_turn(self):
        prev_subject = self.overlay_menu['new'].choose_turn_butt.text().split(' ')[0]
        subject = 'Bot' if prev_subject == 'Human' else 'Human'
        self.overlay_menu['new'].choose_turn_butt.setText(subject + ' goes first!')
        self.first_turn_changed.emit(subject)

    def _change_bot_algo(self, text: Literal['Minimax', 'Monte Carlo Tree Search'],
                         where: Literal['new', 'settings']):
        sync = 'new' if where != 'new' else 'settings'
        if self.overlay_menu[sync].algo_box.currentText() != text:
            self.overlay_menu[sync].algo_box.blockSignals(True)
            self.overlay_menu[sync].algo_box.setCurrentText(text)
            self.overlay_menu[sync].algo_box.blockSignals(False)

        self.bot_algo_changed.emit(text)

    def _ingame_menu_popup(self, tab_index: int):
        if tab_index == 0:
            self.overlay_menu['in-game'].setHidden(False)
        elif tab_index == 1:
            self.overlay_menu['settings'].setHidden(False)


    def _start_game(self, new_game: bool):
        self.game_about_to_start.emit(new_game)

        if new_game:
            hidden_state = self.overlay_menu['new'].isHidden()
            self.overlay_menu['new'].setHidden(not hidden_state)
        self.overlay_menu['in-game'].setHidden(True)
        self.overlay_menu['settings'].setHidden(True)