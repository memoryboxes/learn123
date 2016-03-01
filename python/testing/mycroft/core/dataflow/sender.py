#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import re
import time
import itertools
from .msg import BtrMsgParser,BarMsgParser
from .senderbase import MsgMutilSender

class BtrMsgMutilSender(MsgMutilSender):

    def __init__(self, zmq_socket, instance_id, send_endpoint, files):
        """
        Args:
            ctx: zmq_context

            instance_id: spv instance_id, you can get it by instances_id collection

            send_endpoint: 'tcp://127.0.0.1:23200':

            files:[
                    '/opt/mycroft/tests/fixtures/btr/app1/intf1/201501010000_0.btr.pack',
                    '/opt/mycroft/tests/fixtures/btr/app1/intf1/201501010000_1.btr.pack',
                    ...
                  ]
        """
        self._files = sorted(files)
        self._zmq_socket = zmq_socket
        self._instance_id = int(instance_id)
        self._send_endpoint = send_endpoint

    def  send(self):
        self._zmq_socket.connect(self._send_endpoint)

        for k, g in itertools.groupby(self._files, key=lambda x:'_'.join(x.split('_')[:-1])):
            for file in list(g):
                thread_id = re.match('(\d+)_(\d+|\S+)(.btr.pack|.btr.json|.ntr.pack|.ntr.json)',
                                     os.path.basename(file)).groups()[1]
                if not thread_id.isdigit():
                    thread_id = 0
                self._msg_send(thread_id,file)

        self._zmq_socket.close()

    def _msg_send(self, thread_id, file_name):
        start = time.time()
        self._thread_id = int(thread_id)
        self._file_name = file_name
        msg_count = 0
        msgparser = BtrMsgParser(self._instance_id,
                             self._thread_id,
                             self._file_name)
        if self._file_name.endswith('json'):
            msgs = msgparser.parse('json')
        else:
            msgs = msgparser.parse()

        for msg in msgs:
            self._zmq_socket.send_multipart(msg)
            msg_count += 1
            if msg_count %1000 == 0:
                print("instance_id[%d] thread_id[%d] send_endpoint[%s], send %d msg" %(
                                                                    self._instance_id,
                                                                    self._thread_id,
                                                                    self._send_endpoint,
                                                                    msg_count))

        end = time.time()
        print("instance[%d] thread_id[%d] send_endpoint:[%s], file_name:[%s], send %d msg, took %s" %(
                                                                    self._instance_id,
                                                                    self._thread_id,
                                                                    self._send_endpoint,
                                                                    self._file_name,
                                                                    msg_count,
                                                                    end-start))


class BarMsgMutilSender(MsgMutilSender):

    def __init__(self, zmq_socket, send_endpoint, files, app, intf, workcount):

        self._files = sorted(files)
        self._zmq_socket = zmq_socket
        self._send_endpoint = send_endpoint
        self._app = app
        self._intf = intf
        self._workcount = workcount
        self._work_id = 0

    def  send(self):
        self._zmq_socket.connect(self._send_endpoint)
        for file in self._files:
            self._msg_send(file)
        self._zmq_socket.close()

    def _msg_send(self, file_name):
        start = time.time()
        self._file_name = file_name
        msg_count = 0
        msgparser = BarMsgParser(self._work_id,
                             self._file_name,
                             self._app,
                             self._intf,
                             self._workcount)

        for header, msg in msgparser.parse():
            self._zmq_socket.send_multipart((header, msg))
            msg_count += 1
            if msg_count %1000 == 0:
                print("work_id[%d] send_endpoint[%s], send %d msg" %(
                                                                    self._work_id,
                                                                    self._send_endpoint,
                                                                    msg_count))

        end = time.time()
        print("work_id[%d] send_endpoint:[%s], file_name:[%s], send %d msg, took %s" %(
                                                                    self._work_id,
                                                                    self._send_endpoint,
                                                                    self._file_name,
                                                                    msg_count,
                                                                    end-start))