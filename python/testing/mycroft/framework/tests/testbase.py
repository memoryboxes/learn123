#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from mycroft.framework.base import BaseTestCase
from mycroft.framework.command.base import DiffCommand

class TestBaseTestCase(BaseTestCase):

    def setUp(self):
        super(TestBaseTestCase, self).setUp()

    def test_diff(self):
        for diffcmd in self.get_cmds_by_type(DiffCommand):
            with self.assertRaises(AssertionError):
                diffcmd.assertDiff()

    def test_supervisor(self):
        supervisorctl = self.get_vm('test_create_vm1_for_mycroft_own').supervisor

        supervisorctl.stop('heartbeat')
        self.assertEqual('STOPPED',
                         self._get_all_process_status(supervisorctl)['heartbeat'])

        supervisorctl.start('heartbeat')
        self.assertEqual('RUNNING',
                         self._get_all_process_status(supervisorctl)['heartbeat'])

    def _get_all_process_status(self, supervisorctl):
        all_process = supervisorctl.all_process()
        all_process_status = {}
        for process in all_process:
            all_process_status[process.name] = process.statename
        return all_process_status

    def _get_process_status(self, process_name, supervisorctl):
        pass

    def tearDown(self):
        super(TestBaseTestCase, self).tearDown()
