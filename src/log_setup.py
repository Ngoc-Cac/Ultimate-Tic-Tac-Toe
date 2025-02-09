import logging as lg
import os.path as osp

from logging.handlers import RotatingFileHandler
from pathlib import Path
"""
Code for configuring logging system throughout the whole application.
Firstly, a root logger is configured to NOTSET logging level. This means that
EVERY logging messages of ANY logging level is processed by the root logger.
Secondly, RotatingFileHandlers are created to handle logging messages for 
each corresponding level. This does not exactly filter messages specific to
each levels, but rather filter the messages that satisfy a minimum logging
level. For example, all messages of logging level INFO and above gets written
to info.log.
Lastly, after creating the handlers, each of them is added to the root logger.

To setup, just import this file. Afterwards, call logging.getLogger(__name__)
to create a logger and just log away.
"""

ROOT_DIR = osp.abspath(osp.dirname(__file__))
log_dir = osp.join(ROOT_DIR, 'logs')
if not osp.exists(log_dir):
    Path(log_dir).mkdir()
# set root logger to NOTSET, so all log messages from any other logger is processed
# check setLevel section for more info
# https://docs.python.org/3/library/logging.html
root_logger = lg.getLogger()
root_logger.setLevel(lg.NOTSET)


FORMATTER = lg.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s:\n\t%(message)s')


handler_args: list[int, str] = [
    (lg.DEBUG, "debug"),
    (lg.INFO, "info"),
    (lg.WARNING, "warning"),
    (lg.ERROR, "error"),
    (lg.CRITICAL, "critical")]

for level, name in handler_args:
    handler = RotatingFileHandler(osp.join(log_dir, f'{name}.log'),
                                  maxBytes=2000000,
                                  backupCount=3,
                                  encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(FORMATTER)
    root_logger.addHandler(handler)