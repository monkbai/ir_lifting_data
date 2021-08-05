from src.utils.config import LOG_ON
import sys


class LogType(enumerate):
    INFO = 0,
    RUN_CMD = 1,
    WARNING = 2,
    ERROR = 3


_TYPES = {LogType.INFO: 'INFO', LogType.RUN_CMD: 'RUN CMD', LogType.WARNING: 'WARNING', LogType.ERROR: 'ERROR'}


def log(info: str, log_type=LogType.INFO, _on=LOG_ON):
    if _on:
        print(_TYPES[log_type] + ':\t' + info, file=sys.stderr)
