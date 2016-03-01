#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from .base import BaseCommand, DiffCommand
from mycroft.core.datastore.config import DBConfig, DataStore
from mycroft.core.datastore.api import DatabaseSuite

class MongoImportCommand(BaseCommand):

    def __init__(self, hostip,
                       datastore_path,
                       dropfirst=True,
                       cmd_des="mongo import execute:"):
        self._datastore = DataStore(DBConfig(hostip))
        self._database = DatabaseSuite(self._datastore, datastore_path)
        self._dropfirst = dropfirst
        super(MongoImportCommand, self).__init__(
                "{}, db_path:{}, mongohost:{}".format(
                                        cmd_des,
                                        datastore_path,
                                        hostip
                                    )
                )

    def execute(self):
        self._database.syncdb(dropfirst=self._dropfirst)

class MongoDiffCommand(DiffCommand):
    def __init__(self, hostip,
                       datastore_path,
                       exclude,
                       auto_format,
                       cmd_des="mongo diff object construct"):
        self._datastore = DataStore(DBConfig(hostip))
        self._database = DatabaseSuite(self._datastore, datastore_path)
        self._exclude = exclude
        self._auto_format = auto_format
        super(MongoDiffCommand, self).__init__(
                "{}, db_path:{}, mongohost:{}".format(
                                        cmd_des,
                                        datastore_path,
                                        hostip
                                    )
                )

    def execute(self):
        pass

    def assertDiff(self):
        self._database.diff(self._exclude, self._auto_format)

class MongoDisorderDiffCommand(DiffCommand):
    def __init__(self, hostip,
                       datastore_path,
                       exclude,
                       auto_format,
                       cmd_des="mongo diff object construct"):
        self._datastore = DataStore(DBConfig(hostip))
        self._database = DatabaseSuite(self._datastore, datastore_path)
        self._exclude = exclude
        self._auto_format = auto_format
        super(MongoDisorderDiffCommand, self).__init__(
                "{}, db_path:{}, mongohost:{}".format(
                                        cmd_des,
                                        datastore_path,
                                        hostip
                                    )
                )

    def execute(self):
        pass

    def assertDiff(self):
        self._database.diffdisorder(self._exclude, self._auto_format)

class MongoCleanCommand(MongoImportCommand):
    def __init__(self, hostip, datastore_path, cmd_des="mongo clean execute"):
        super(MongoCleanCommand, self).__init__(
                                               hostip,
                                               datastore_path,
                                               cmd_des=cmd_des
                                              )

    def execute(self):
        self._database.clean()
