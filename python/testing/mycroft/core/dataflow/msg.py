#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import json
import msgpack
from .msgbase import MsgParser

class BtrMsgParser(MsgParser):

    def __init__(self, instance_id, thread_id, file_name):
        self._instance_id = instance_id
        self._thread_id = thread_id
        self._file_name = file_name
        super(BtrMsgParser, self).__init__()

    def parse(self, msgtype='msgpack'):
        with open(self._file_name, 'rb') as stream:
            if msgtype == 'msgpack':
                unpacker = msgpack.Unpacker(stream)
            elif msgtype == 'json':
                unpacker = json.load(file(self._file_name, 'r'))
            else:
                raise ValueError('unsupported msgtype')

            for msg in unpacker:
                header = msgpack.packb(self.make_header(msg))
                yield header, msgpack.packb(msg)

    def make_header(self,msg):
        flow_id = msg.get('FlowId')
        if flow_id:
            hash_key = hash('%s_%s' % (self._instance_id, flow_id))
        else:
            hash_key = 0
        return [msg['ts'] / 1000000000, msg['ts'] % 1000000000, self._instance_id, self._thread_id, hash_key, 0]


class BarMsgParser(MsgParser):

    def __init__(self, work_id, file_name, app, intf, workcount):
        self._work_id = work_id
        self._file_name = file_name
        self._app = app
        self._intf = intf
        self._workcount = workcount
        super(BarMsgParser, self).__init__()

    def parse(self, msgtype='msgpack'):
        time = []
        with open(self._file_name, 'rb') as stream:
            if msgtype == 'msgpack':
                unpacker = msgpack.Unpacker(stream)
            elif msgtype == 'json':
                unpacker = json.load(file(self._file_name, 'r'))
            else:
                raise ValueError('unsupported msgtype')

            for msg in unpacker:
                time.append(msg['ts'])
                header = msgpack.packb(self.make_header(msg))
                yield header, msgpack.packb(msg)

            for work_id in xrange(0, self._workcount):
                yield (msgpack.packb({
                 'app': self._app,
                 'intf': self._intf,
                 'worker_thread_id': work_id,
                 'ts': time[-1],
                 }),
                 msgpack.packb({
                 'ts': time[-1],
                 'ts_end': time[-1],
                 'DP#SYNC': 'DP#SYNC',
                 'complete_ts': time[-1],
                 })
                )


    def make_header(self,msg):
        header = {
                    'app': self._app,
                    'intf': self._intf,
                    'worker_thread_id': self._work_id,
                    'ts': msg['ts']
                }
        return header
