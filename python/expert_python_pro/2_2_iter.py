#!/bin/env python
# -*- coding: utf-8 -*-

class MyIterator(object):

    def __init__(self, step):
        self.step = step

    def next(self):
        if self.step == 0:
            raise StopIteration
        self.step -= 1
        return self.step

    def __iter__(self):
        return self

for el in MyIterator(10):
    print el
