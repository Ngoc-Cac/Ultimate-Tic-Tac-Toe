import sys

from PyQt6.QtWidgets import QApplication

from GUI.main_window import MainWindow


import logging as lg
logger = lg.getLogger(__name__)
"""
Code handling execution of application
"""


def main() -> int:
    # sys.argv += ['-platform', 'windows:darkmode=1'] for testing light and dark theme
    ult_tictactoe = QApplication(sys.argv)
    ult_tictactoe.setStyle('QtCurve')

    root = MainWindow(ult_tictactoe)

    logger.info('Starting game...')
    root.show()
    exit_code = ult_tictactoe.exec()
    logger.info(f'Exited successfully with code {exit_code}')
    return exit_code