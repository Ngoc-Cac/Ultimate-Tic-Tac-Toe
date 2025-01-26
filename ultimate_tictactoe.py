import GUI.main_task
import log_setup # import the module to the set up tasks for logging
import logging as lg
import sys
from traceback import format_exception


logger = lg.getLogger(__name__)

# set up except hook to handle any exceptions while running the event loop
def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(format_exception(exc_type, exc_value, exc_tb))
    logger.critical(f'Program exited due to exception:\n{tb}')
    logger.info('Exited with code 1')
    sys.exit(1)

sys.excepthook = except_hook


import GUI
exit_code = GUI.main_task.main()
sys.exit(exit_code)