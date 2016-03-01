#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import tempfile
from unittest import main, TestCase

from mycroft.core.client.machine import VMachine
from mycroft.core.datastore.config import DBConfig, DataStore
from mycroft.core.datastore.api import DatabaseSuite
from mycroft.settings import TEST_VM_HOST

fixture_sync = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), 'fixtures/test_datastore/db'))
fixture_diffA = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), 'fixtures/test_datastore/diffdbA'))
fixture_diffB = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), 'fixtures/test_datastore/diffdbB'))

class DatastoreTestCase(TestCase):

    def setUp(self):
        super(DatastoreTestCase, self).setUp()
        self.vm = self._get_new_vm()
        self.vm.create()
        self.vm.execute('/etc/init.d/mongod start')

        self._datastore = DataStore(DBConfig(self.vm.ip))

    def test_syncdb(self):
        database = DatabaseSuite(self._datastore, fixture_sync)
        database.syncdb(dropfirst=True)
        database.diff(['ts_sys'], True)

    def test_diff(self):
        databaseA = DatabaseSuite(self._datastore, fixture_diffA)
        databaseA.syncdb(dropfirst=True)
        databaseB = DatabaseSuite(self._datastore, fixture_diffB)
        databaseB.diff(['ts_sys', 'min', 'max'], True)

    def tearDown(self):
        self.vm.delete()
        super(DatastoreTestCase, self).tearDown()

    def _get_new_vm(self):
        TEST_VM_HOST['project'] = 'bpc3'
        return VMachine(**TEST_VM_HOST)
