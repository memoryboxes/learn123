#!/usr/bin/env python
#  -*- coding: utf-8 -*-

def retry(ExceptionToCheck, try_count):

    def deco_retry(fn):
        def wrapper(*args, **kwargs):
            _try_count = try_count

            while _try_count > 1:
                try:
                    return fn(*args, **kwargs)
                except ExceptionToCheck, e:
                    print e.message
                    _try_count -= 1
            return fn(*args, **kwargs)

        return wrapper

    return deco_retry
