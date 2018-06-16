# -*- coding: utf-8 -*-

import logging
import logging.handlers
import sys


class MiniLogger(object):
    LEVEL_FULL_FORMAT = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    LEVEL_SIMPLE_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
    LEVEL_NONE_FORMAT = '%(message)s'

    DEFAULT_LEVEL = logging.DEBUG
    DEFAULT_LEVEL_FORMAT = LEVEL_FULL_FORMAT
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, name='minilogger',
                 level=DEFAULT_LEVEL,
                 level_format=DEFAULT_LEVEL_FORMAT,
                 date_format=DEFAULT_DATE_FORMAT):
        self._name = name
        self._logger = logging.getLogger(name)
        self._level = level
        self._level_format = level_format
        self._date_format = date_format

        # Set default log level
        self._logger.setLevel(self._level)

    def stream_logger(self, out=sys.stdout):
        ch = logging.StreamHandler(out)
        ch.setLevel(self._level)

        # create formatter
        formatter = logging.Formatter(self._level_format)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        # The final log level is the higher one between the default and the one in handler
        self._logger.addHandler(ch)
        return self._logger

    def file_logger(self, file=None):
        if file is None:
            file = self._name + '.log'
        ch = logging.FileHandler(file)
        ch.setLevel(self._level)

        formatter = logging.Formatter(self._level_format)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

        return self._logger

    def rotating_file_logger(self, file=None,
                             max_bytes=1024 * 1024 * 1024,
                             backup_count=10):
        if file is None:
            file = self._name + '.log'
        ch = logging.handlers.RotatingFileHandler(file,
                                                  maxBytes=max_bytes,
                                                  backupCount=backup_count)
        ch.setLevel(self._level)

        formatter = logging.Formatter(self._level_format)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

        return self._logger


def test_logger(logger):
    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')


if __name__ == '__main__':
    logger = MiniLogger().stream_logger()
    test_logger(logger)
    logger = MiniLogger().stream_logger(sys.stderr)
    test_logger(logger)

    logger = MiniLogger(level_format='%(message)s').stream_logger()
    test_logger(logger)

    logger = MiniLogger(level_format='%(message)s').file_logger('minilogger.log')
    test_logger(logger)

    logger = MiniLogger(level_format='%(message)s').rotating_file_logger(max_bytes=1024 * 1024)
    for i in range(10000):
        test_logger(logger)
