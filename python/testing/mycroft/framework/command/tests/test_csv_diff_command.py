'''
Created on Sep 6, 2015

@author: evajiang
'''
from unittest import TestCase

from mycroft.core.client.machine import VMachine
from mycroft.settings import TEST_VM_HOST, PROJECT_ROOT
from mycroft.framework.command.file import FileDiffOfCSVCommand, FilePutCommand
from mycroft.core.datastore.errors import AssertionTextDiffError, AssertionJsonDiffError
import os

class FileDiffOfCSVCommandTestCase(TestCase):

    def setUp(self):
        super(FileDiffOfCSVCommandTestCase, self).setUp()
        self.vm = VMachine(**TEST_VM_HOST)
        self.local_path = os.path.join(PROJECT_ROOT, "framework/command/tests/fixture/csv/local")
        self.local_remote_path = os.path.join(PROJECT_ROOT, "framework/command/tests/fixture/csv/local_remote")
        self.remote_path = os.path.join("/tmp")

    def test_file_diff_of_csv_command(self):
        self.vm.create()
        FilePutCommand(self.vm, self.local_remote_path, self.remote_path).execute()
        diff = FileDiffOfCSVCommand(self.vm, self.local_path, "%s/local_remote" % self.remote_path)
        diff.execute()
        try:
            diff.assertDiff()
            self.assertTrue(False)
        except AssertionTextDiffError:
            diff._fileclean()
            return True

    def tearDown(self):
        self.vm.delete()
        super(FileDiffOfCSVCommandTestCase, self).tearDown()
