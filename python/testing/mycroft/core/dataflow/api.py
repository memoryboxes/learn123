#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import zmq
import glob
import itertools
from .sender import MsgMutilSender

class DataflowSuite(object):

    def __init__(self, datastore, dataflow_path, send_endpoints, project='bpc'):
        """

        Args:
            datastore: mongo datastore

            dataflow_path: your fixture dataflow file path
            for exp: fixture/test_alert/dataflow/btr
                     fixture|
                            |-test_alert|
                            |           |-dataflow|
                            |                     |-btr|app1|
                                                            |intf1|
                                                                  |-201501010000_0.btr.pack
                                                                  |-201501010000_1.btr.pack

            DataflowSuite will scan `fixture/test_alert/dataflow/btr` and gen dataflow sender config
        """
        ctx = zmq.Context()
        self._socket = ctx.socket(zmq.PUSH)
        self._dataflow_path = dataflow_path
        self._send_endpoints = send_endpoints
        self._project = project

    def send(self):
        for instance, send_endpoint in zip(self._instances(), self._send_endpoints):
            MsgMutilSender(self._socket,
                           instance['instance_id'],
                           send_endpoint,
                           glob.glob(os.path.join(self._dataflow_path, instance['app'], instance['intf']))).send()

    def _instances(self):
        """
        Return:
            [
                {'app':'app1', 'intf':'intf1', 'instance_id':xxxxxxx, 'endpoints'},
                {'app':'app1', 'intf':'intf2', 'instance_id':xxxxxxx},
                {'app':'app1', 'intf':'intf3', 'instance_id':xxxxxxx},
            ]
        """
        app_dirs = glob.iglob(os.path.join(self._dataflow_path, '*'))
        app_dirs = (os.basename(x) for x in app_dirs if os.path.isdir(x))

        all_instances = []
        if self._project == 'bpc':
            for record in self._datastore.conn['bpc']['instance_id'].find({}):
                all_instances.append({
                                        'instance_id':record['instance_id'],
                                        'app':record['app_name'],
                                        'intf':record['intf_name'],
                                     }
                                    )
        for app in app_dirs:
            intf_dirs = glob.iglob(os.path.join(self._dataflow_path, app, '*'))
            intf_dirs = (os.basename(x) for x in intf_dirs if os.path.isdir(x))

            for intf in intf_dirs:
                for instance in all_instances:
                    if instance['app'] == app and instance['intf'] == intf:
                        yield instance
                raise ValueError('Not find matched instance_id:%s, %s' % (app, intf))
