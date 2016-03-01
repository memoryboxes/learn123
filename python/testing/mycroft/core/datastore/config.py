#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import io
import json
from pymongo import MongoClient

class DBConfig(object):

    def __init__(self, host, port=27017, username=None, password=None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

class DataStore(object):

    def __init__(self, db_config):
        self._db_config = db_config
        self._conn = self._connect()

    def _connect(self):
        if self._db_config.username != None and self._db_config.password != None:
            mongodb_uri = 'mongodb://%s:%s@%s:%d' % (
                                                        self._db_config.username,
                                                        self._db_config.password,
                                                        self._db_config.host,
                                                        self._db_config.port)
        else:
            mongodb_uri = 'mongodb://%s:%d' % (self._db_config.host,
                                               self._db_config.port)
        c = MongoClient(mongodb_uri)
        return c

    @property
    def config(self):
        return self._db_config

    @property
    def conn(self):
        return self._conn

    def get_db(self, db_name):
        self._conn[db_name]

    def get_db_names(self):
        return self._conn.database_names()

