#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from sh import ifconfig

class TestException(Exception):

    def __init__(self, msg, errno=1):
        self._message = msg
        self._errno = errno

    def __str__(self):
        return "{}{}".format(self._message, self._errno)

    @property
    def message(self):
        return self._message

    @property
    def errno(self):
        return self._errno

def testerror():
    raise TestException("hello, exception")

try:
    #ifconfig('ethzzzzz')
    testerror()
except Exception as e:
    print "{}, {}".format(e.message, e.errno)
    print e
