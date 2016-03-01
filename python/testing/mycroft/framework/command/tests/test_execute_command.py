#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from unittest import TestCase

from mycroft.core.client.machine import VMachine
from mycroft.settings import TEST_VM_HOST
from mycroft.framework.command.execute import ExecuteCommand

class ExecuteCommandTestCase(TestCase):

    def setUp(self):
        super(ExecuteCommandTestCase, self).setUp()
        self.vm = self._get_new_vm()
        self._cmd = 'ifconfig'

    def test_execute_command(self):
        self.vm.create()
        remote_ip= self._execute_command().execute()
        self.assertTrue(self.vm.ip in remote_ip)

    def tearDown(self):
        self.vm.delete()
        super(ExecuteCommandTestCase, self).tearDown()

    def _get_new_vm(self):
        return VMachine(**TEST_VM_HOST)

    def _execute_command(self):
        return ExecuteCommand(self.vm, self._cmd)