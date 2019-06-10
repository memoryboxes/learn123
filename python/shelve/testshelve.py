# -*- coding: utf-8 -*-
import shelve
import dbm
from contextlib import closing

import shelvex

if __name__ == '__main__':
    with closing(shelve.open('db', writeback=True)) as db:
        print([key for key in db.keys()])

    print(dbm.whichdb('db'))

    with closing(shelvex.open('db2', writeback=True)) as db:
        print([key for key in db.keys()])

    print(dbm.whichdb('db2'))
