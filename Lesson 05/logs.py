# app_logger.py
import logging
import logging.handlers
import os
import sys

_log_format = f"%(asctime)24s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


class Log:
    def __init__(self, file_name='', module_name='default'):
        self._file_name = file_name

        self._file_handler = logging.FileHandler(self._file_name)
        self._file_handler.setLevel(logging.DEBUG)
        self._file_handler = logging.handlers.TimedRotatingFileHandler(os.path.abspath(self._file_name),
                                                                       encoding='utf8', interval=1, when='D')
        self._file_handler.setFormatter(logging.Formatter(_log_format))

        self._stream_handler = logging.StreamHandler(sys.stdout)
        self._stream_handler.setLevel(logging.INFO)
        self._stream_handler.setFormatter(logging.Formatter(_log_format))

        self._logger = logging.getLogger(module_name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(self._file_handler)
        self._logger.addHandler(self._stream_handler)

    @property
    def get_logger(self):
        return self._logger


if __name__ == "__main__":
    sl = Log('server.log').get_logger
    sl.info("Info message test.")
    sl.warning("Warning message test.")
    sl.debug("Debug message test.")
