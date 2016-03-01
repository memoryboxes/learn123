#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from unittest import TestCase

from mycroft.core.client.machine import VMachine
from mycroft.settings import TEST_VM_HOST
from mycroft.framework.command.file import FilePutCommand,FileGetCommand
import os
import tempfile
import shutil

class FileCommandTestCase(TestCase):

    def setUp(self):
        super(FileCommandTestCase, self).setUp()
        self.vm = self._get_new_vm()
        self._fixture_file_path = os.path.abspath(__file__)
        self._fixture_file_name = os.path.basename(__file__)
        self._fixture_remote_path = os.path.join(tempfile.gettempdir(),self._fixture_file_name)
        self._tempdir = tempfile.mktemp()
        self._tempfile_path = os.path.join(self._tempdir, os.path.basename(__file__))

    def test_put_file_command(self):
        self.vm.create()
        self._put_file_command().execute()
        self.assertTrue(self.vm.checkfile_exists(self._fixture_remote_path))

    def test_get_file_command(self):
        self.vm.create()
        self._put_file_command().execute()
        self._get_file_command().execute()
        self.assertTrue(os.path.exists(self._tempfile_path))
        shutil.rmtree(self._tempdir)

    def tearDown(self):
        self.vm.delete()
        super(FileCommandTestCase, self).tearDown()

    def _get_new_vm(self):
        return VMachine(**TEST_VM_HOST)

    def _put_file_command(self):
        return FilePutCommand(self.vm, self._fixture_file_path, self._fixture_remote_path)

    def _get_file_command(self):
        return FileGetCommand(self.vm, self._tempfile_path, self._fixture_remote_path)


