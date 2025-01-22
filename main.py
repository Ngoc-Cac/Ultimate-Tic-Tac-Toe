import log_setup
import logging as lg
import sys
from traceback import format_exception


from PyQt6.QtWidgets import QApplication

from GUI.main_window import MainWindow


logger = lg.getLogger(__name__)

def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(format_exception(exc_type, exc_value, exc_tb))
    logger.critical(f'Program exited due to exception:\n{tb}')
    logger.info('Exited with code 1')
    sys.exit(1)

sys.excepthook = except_hook


ult_tictactoe = QApplication([])
root = MainWindow(ult_tictactoe)

logger.info('Starting...')
root.show()

exit_code = ult_tictactoe.exec()
logger.info(f'Exited successfully with code {exit_code}')
sys.exit(exit_code)