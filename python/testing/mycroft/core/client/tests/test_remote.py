#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import time
import tempfile
from unittest import main, TestCase

from mycroft.core.client.remote import (RemoteEnv,
                      PutFileToRemoteTask,
                      CheckFileExistsRemoteTask,
                      DelFileFromRemoteTask,
                      GetFileFromRemoteTask,
                      RunInRemoteTask)
from mycroft.core.client.machine import VMachine, VMStatus
from mycroft.settings import TEST_VM_HOST

fixture_file_path = os.path.abspath(__file__)
fixture_file_name = os.path.basename(__file__)

class RemoteActionTestCase(TestCase):

    def setUp(self):
        super(RemoteActionTestCase, self).setUp()
        self._fixture_remote_path = os.path.join(tempfile.gettempdir(),
                                                 fixture_file_name)
        self.vm = self._get_new_vm()
        self.env = RemoteEnv(self.vm.ip, self.vm.user, self.vm.password)

    def test_put_file(self):
        self.vm.create()
        self.vm.putfile(fixture_file_path, self._fixture_remote_path)
        self.assertTrue(self.vm.checkfile_exists(self._fixture_remote_path))

    def test_get_file(self):
        self.vm.create()
        self.vm.putfile(fixture_file_path, self._fixture_remote_path)

        tempfile_path = os.path.join(tempfile.mktemp(), os.path.basename(__file__))
        self.vm.getfile(self._fixture_remote_path, tempfile_path)

        self.assertTrue(os.path.exists(tempfile_path))
        os.remove(tempfile_path)

    def test_run_ifconfig(self):
        self.vm.create()
        remote_ip_info = self.vm.execute('ifconfig')
        self.assertTrue(self.env.host in remote_ip_info)

    def tearDown(self):
        self.vm.delete()
        super(RemoteActionTestCase, self).tearDown()

    def _get_new_vm(self):
        return VMachine(**TEST_VM_HOST)

