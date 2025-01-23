import logging as lg
import os.path as osp

from logging.handlers import RotatingFileHandler

# set root logger to NOTSET, so all log messages from any other logger is processed
# check setLevel section for more info
# https://docs.python.org/3/library/logging.html

log_dir = osp.join('.', 'logs')

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