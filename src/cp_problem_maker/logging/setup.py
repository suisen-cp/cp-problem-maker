import logging
from enum import Enum
from logging.handlers import RotatingFileHandler

import colorlog

from cp_problem_maker import anchor


class LogLevelEnum(Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


_LOG_FORMAT = "%(log_color)s[%(levelname)s]:%(name)s:%(message)s"
_LOG_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

_CONSOLE_HANDLER = colorlog.StreamHandler()
_CONSOLE_HANDLER.setFormatter(
    colorlog.ColoredFormatter(_LOG_FORMAT, log_colors=_LOG_COLORS)
)
_CONSOLE_HANDLER.setLevel(LogLevelEnum.INFO.value)

_FILE_HANDLER = RotatingFileHandler(
    str(anchor.SOURCE_ROOT / "data/log/cp_problem_maker.log"),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
_FILE_HANDLER.setFormatter(
    logging.Formatter("%(asctime)s - [%(levelname)s]:%(name)s:%(message)s")
)
_FILE_HANDLER.setLevel(LogLevelEnum.DEBUG.value)


def get_logger(name: str) -> logging.Logger:
    logger = colorlog.getLogger(name)
    logger.addHandler(_CONSOLE_HANDLER)
    logger.addHandler(_FILE_HANDLER)
    logger.setLevel(LogLevelEnum.DEBUG.value)
    return logger
