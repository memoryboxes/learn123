#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import zmq
import glob
import json
import itertools
import threading

from mycroft.core.dataflow.sender import BtrMsgMutilSender,BarMsgMutilSender
from mycroft.utils.shutilv import strip_folders
from .base import BaseCommand

class ZMQSendCommand(BaseCommand):
    def __init__(self, send_endpoint,
                       datastore_path,
                       instance_id,
                       workcount):
        ctx = zmq.Context()
        self._socket = ctx.socket(zmq.PUSH)
        self._files = glob.glob(os.path.join(datastore_path, '*'))
        self._send_endpoint = send_endpoint
        self._workcount = workcount
        app_path = os.path.split(datastore_path)[0]
        self._intf = os.path.split(datastore_path)[-1]
        self._app = os.path.split(app_path)[-1]
        self._flag = os.path.split(os.path.split(app_path)[0])[-1]
        if "btr" in self._flag:
            self._sender = BtrMsgMutilSender(self._socket,
                                      instance_id,
                                      self._send_endpoint,
                                      self._files
                                      )
        elif "bar" in self._flag:
            self._sender = BarMsgMutilSender(self._socket,
                                      self._send_endpoint,
                                      self._files,
                                      self._app,
                                      self._intf,
                                      self._workcount
                                      )

        super(ZMQSendCommand, self).__init__(
                cmd_des="zmq sender execute,send msg to {},\n".format(
                                                    self._send_endpoint
                                                )
                )

    def execute(self):
        self._sender.send()

class MultiZMQSendCommand(BaseCommand):

    def __init__(self, send_endpoints,
                       datastore_path,
                       instance_id_json_path,
                       workcount):
        """support apps btr/ntr playback

        Args:
            send_endpoints: endpoints,such ['tcp://127.0.0.1:23000', ...]
            datastore_path: your fixture db file path
                for exp:
                   fixtures/btr/app1/intfxxx
                                    |...
                   fixtures/btr/app2/intfxxx
                                    |...
                                ....
            instance_id_json_path: full path of instance_id.json
        """
        self._send_endpoints = send_endpoints
        send_endpoint_cycle = itertools.cycle(send_endpoints)
        self._zmq_send_cmds = []
        instance_ids = []

        with open(instance_id_json_path, 'r') as instance_id_json:
            for line in instance_id_json.readlines():
                instance_ids.append(json.loads(line))

        for app in strip_folders(os.listdir(datastore_path)):
            for intf in strip_folders(os.listdir(os.path.join(datastore_path, app))):
                instance_id = self._get_instance_id(instance_ids, app, intf)
                self._zmq_send_cmds.append(ZMQSendCommand(
                                                    send_endpoint_cycle.next(),
                                                    os.path.join(datastore_path, app, intf),
                                                    instance_id,
                                                    workcount)
                                            )


        super(MultiZMQSendCommand, self).__init__(
                cmd_des="app zmq sender execute,send msg of {} to {},\n".format(
                                                    datastore_path,
                                                    ' '.join(self._send_endpoints)
                                                )
                )

    def execute(self):
        send_threads = []
        for send_cmd in self._zmq_send_cmds:
            send_threads.append(threading.Thread(target=send_cmd.execute))

        for send_thread in send_threads:
            send_thread.start()
        for send_thread in send_threads:
            send_thread.join()

    def _get_instance_id(self, records, app, intf):
        for record in records:
            if record['app_name'] == app and \
               record['intf_name'] == intf:
                return record['instance_id']
        raise ValueError("Don't find valid instance_id for {}:{}".format(app, intf))
