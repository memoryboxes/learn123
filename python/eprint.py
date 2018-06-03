# -*- coding: utf-8 -*-

from __future__ import print_function
import sys


def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    # Test
    print("Test")

    # Test
    eprint("Test")

    # foo---bar---baz
    eprint("foo", "bar", "baz", sep="---")
