import logging
import sys


class Formatter(logging.Formatter):
    """vu1-monitor logging format"""

    def format(self, record: logging.LogRecord):
        """format record"""
        if record.levelno > 0:
            self._style._fmt = "%(asctime)-15s - %(name)s - %(levelname)s - %(message)s"
        return super().format(record)


def create_logger(name: str, level: int | str = logging.INFO) -> logging.Logger:
    """Create a logger instance

    :param name: name of logger
    :return: logger instnace
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(Formatter())

    logger.addHandler(stream_handler)
    return logger
