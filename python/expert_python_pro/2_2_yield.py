#!/bin/env python
# -*- coding: utf-8 -*-

def fibonacci():
    a, b = 0, 1
    while True:
        yield b
        a, b = b, a + b

fib = fibonacci()
fib.next()
fib.next()
print [fib.next() for i in xrange(10)]
