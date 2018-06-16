# -*- coding: utf-8 -*-

import logging
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
        ch2 = logging.FileHandler(file)
        ch2.setLevel(self._level)

        formatter = logging.Formatter(self._level_format)
        ch2.setFormatter(formatter)
        self._logger.addHandler(ch2)

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

    logger = MiniLogger(level_format='%(message)s').file_logger('process.log')
    test_logger(logger)
