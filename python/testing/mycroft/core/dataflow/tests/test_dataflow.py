#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import zmq
import time
from unittest import TestCase

from mycroft.core.client.machine import VMachine
from mycroft.core.datastore.config import DBConfig, DataStore
from mycroft.core.dataflow.sender import BtrMsgMutilSender,BarMsgMutilSender
from mycroft.settings import TEST_VM_HOST

btr_file_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), 'fixtures/test_dataflow/btr'))
bar_file_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), 'fixtures/test_dataflow/bar'))

class DataflowTestCase(TestCase):

    def setUp(self):
        super(DataflowTestCase, self).setUp()
        self.vm = self._get_new_vm()
        self.vm.create()
        self.vm.execute('/usr/local/bin/bpctt setup')

        ctx = zmq.Context()
        self._socket = ctx.socket(zmq.PUSH)
        self._datastore = DataStore(DBConfig(self.vm.ip))
        self._btrsender = BtrMsgMutilSender(self._socket,
                                      123,
                                      "tcp://%s:23200" % self.vm.ip,
                                      [os.path.join(btr_file_path, '20140210130300_intf1.btr.json')])
        self._barsender = BarMsgMutilSender(self._socket,
                                      "tcp://%s:23400" % self.vm.ip,
                                      [os.path.join(bar_file_path, '20140210130800.bar.pack')],
                                      1,
                                      1,
                                      4)

    def test_send_btr(self):
        self._btrsender.send()
        time.sleep(10)

    def test_send_bar(self):
        self._barsender.send()
        time.sleep(10)

    def tearDown(self):
        self.vm.delete()
        super(DataflowTestCase, self).tearDown()

    def _get_new_vm(self):
        TEST_VM_HOST['project'] = 'bpc3'
        return VMachine(**TEST_VM_HOST)
