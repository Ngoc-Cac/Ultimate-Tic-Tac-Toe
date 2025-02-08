import os.path as osp
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from GUI import _ROOT_DIR
from GUI.main_window import MainWindow


import logging as lg
logger = lg.getLogger(__name__)
"""
Code handling execution of application
"""

# give the app an id, this is for the purpose of
# setting the app's icon in taskbar for Windows
try:
    from ctypes import windll
    myappid = u'ultttt.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def main() -> int:
    # sys.argv += ['-platform', 'windows:darkmode=1'] for testing light and dark theme
    ult_tictactoe = QApplication(sys.argv)
    ult_tictactoe.setStyle('QtCurve')
    ult_tictactoe.setWindowIcon(QIcon(osp.join(_ROOT_DIR, 'resource', 'icons', 'app_icon.png')))

    root = MainWindow(ult_tictactoe)

    logger.info('Starting game...')
    root.show()
    exit_code = ult_tictactoe.exec()
    logger.info(f'Exited successfully with code {exit_code}')
    return exit_code