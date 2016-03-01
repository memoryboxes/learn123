#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from unittest import TestCase
from mycroft.core.client.machine import VMachine
from mycroft.settings import TEST_ETH_HOST
from mycroft.core.client.remote import RemoteEnv

class EthsTestCase(TestCase):

    def setUp(self):
        super(EthsTestCase, self).setUp()
        self.vm = self._get_new_vm()
        self.env = RemoteEnv(self.vm.ip, self.vm.user, self.vm.password)

    def test_run_ifconfig(self):
        self.vm.create()
        remote_eths_info = self.vm.execute("""ifconfig""")
        self.assertTrue('eth_test' in remote_eths_info)

    def tearDown(self):
        self.vm.delete()
        super(EthsTestCase, self).tearDown()

    def _get_new_vm(self):
        return VMachine(**TEST_ETH_HOST)