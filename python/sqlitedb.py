# -*- coding: utf-8 -*-

import glob
import os
import sys
import sqlite3


class SqliteConn(object):

    def __init__(self, db):
        self._conn = sqlite3.connect(db)
        self._cursor = self._conn.cursor()

    def insert(self, table, row):
        cols = ', '.join('"{}"'.format(col) for col in row.keys())
        vals = ', '.join(':{}'.format(col) for col in row.keys())
        sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
        self._cursor.execute(sql, row)

    def commit(self):
        self._conn.commit()


if __name__ == '__main__':
    db = SqliteConn('test.db')
    db.insert('passhouse', {
                    'username': 'a',
                    'email': 'b@b.com',
                    'password': 'c'
                }
    )
    db.commit()
