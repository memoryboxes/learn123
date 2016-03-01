'''
Created on Sep 6, 2015

@author: wendy.wang
'''
from unittest import TestCase
from mycroft.settings import PROJECT_ROOT
from mycroft.framework.command.file import FileDiffOfXMLCommand, FilePutCommand
from mycroft.core.datastore.errors import AssertionTextDiffError, AssertionJsonDiffError
import os

class FileDiffOfXMLCommandTestCase(TestCase):

    def setUp(self):
        super(FileDiffOfXMLCommandTestCase, self).setUp()
        

    def test_file_diff_of_xml_command_same(self):
        self.local_path = os.path.join(PROJECT_ROOT, "framework/command/tests/fixture/xml/local/output-5/alerts")
        self.remote_path = os.path.join(PROJECT_ROOT, "framework/command/tests/fixture/xml/remote/output-5/alerts")
        diff = FileDiffOfXMLCommand(self.local_path, self.remote_path)
        diff.execute()
        try:
            same_flag = diff.assertDiff()
            self.assertTrue(same_flag)
        except AssertionTextDiffError:
            return False
            
    def test_file_diff_of_xml_command_diff(self):
        self.local_path = os.path.join(PROJECT_ROOT, "framework/command/tests/fixture/xml/local/output-5/stats")
        self.remote_path = os.path.join(PROJECT_ROOT, "framework/command/tests/fixture/xml/remote/output-5/stats")
        diff = FileDiffOfXMLCommand(self.local_path, self.remote_path)
        diff.execute()
        try:
            diff_flag = diff.assertDiff()
            self.assertFalse(diff_flag)
        except AssertionTextDiffError:
            return False

    def tearDown(self):
        super(FileDiffOfXMLCommandTestCase, self).tearDown()
