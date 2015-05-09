#!/bin/env python
# -*- coding: utf-8 -*-

def _treatment(pos, element):
    return "%d: %s" % (pos, element)

seq = ["one", "two", "three"]
print [_treatment(i, el) for i, el in enumerate(seq)]
