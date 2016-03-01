#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
from unittest import TestCase

from mycroft.configs.config import MycroftConfig

class ConfigTestCase(TestCase):

    base_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), 'fixtures')
                )

    test_single_machine = {
                    'dockerflyd': u'http://172.16.11.13:5123/v1/',
                    'ip': u'172.16.13.31',
                    'autodelete': True,
                    'gateway': u'172.16.13.1',
                    'project': u'bpc3ui',
                    'ActionGroups':
                        {
                            'tearDown': (
                                {
                                    'commands': (
                                        {
                                            'type': u'MongoClean',
                                            'fixture': {
                                                u'path':'importdb',
                                            }
                                        },
                                    )
                                },
                            ),
                          'setUp': (
                            {
                                'commands': (
                                    {
                                        'type': u'MongoImport',
                                        'fixture': {
                                            u'path':'importdb'
                                        }
                                    },
                                    {
                                        'type': u'MongoDiff',
                                        'fixture': {
                                            u'path':'diffdb'
                                        }
                                    },
                                    {
                                        'type': u'ZMQSend',
                                        'fixture': {
                                            u'path':'btr'
                                        },
                                        'send_endpoint':'tcp://127.0.0.1:23000',
                                        'instance_id':'0'
                                    },
                                    {
                                        'type': u'MultiZMQSend',
                                        'fixture': {
                                            u'path':'btr',
                                            u'instance_id_path':'instance_id.json',
                                        },
                                        'send_endpoints':{
                                            'send_endpoint':(
                                                               'tcp://127.0.0.1:23000',
                                                               'tcp://127.0.0.1:23001'
                                                             )
                                        },
                                    },
                                    {
                                        'type': u'FilePut',
                                        'fixture': {
                                            u'path':'putfile',
                                        },
                                        'remote_path':'/test'
                                    },
                                    {
                                        'type': u'FileGet',
                                        'fixture': {
                                            u'path':'getfile',
                                        },
                                        'remote_path':'/test'
                                    },
                                 )
                            },)},
                    'id': u'mycroft_machine_for_bpc3ui',
                    'desc': u'test for bpc3ui'
                }

    test_multi_machine_1 = {
                    'dockerflyd': u'http://172.16.11.13:5123/v1/',
                    'ip': u'172.16.13.31',
                    'autodelete': True,
                    'gateway': u'172.16.13.1',
                    'project': u'bpc3ui',
                    'id': u'mycroft_machine_for_bpc3ui_1',
                    'desc': u'test for bpc3ui'
                }

    test_multi_machine_2 = {'dockerflyd': u'http://172.16.11.13:5123/v1/',
                    'ip': u'172.16.13.31',
                    'autodelete': True,
                    'gateway': u'172.16.13.1',
                    'project': u'bpc3ui',
                    'ActionGroups':
                        {
                          'tearDown': (
                            {
                                'commands': (
                                    {
                                        'type': u'MongoClean',
                                        'fixture': {
                                            'path': 'importdb'
                                        }
                                    },
                                )
                            },
                          ),
                          'setUp': (
                            {
                                'commands': (
                                    {
                                        'type': u'MongoImport',
                                        'fixture': {
                                            'path': 'importdb'
                                        }
                                    },
                                    {
                                        'type': u'MongoDiff',
                                        'fixture': {
                                            'path': 'diffdb'
                                        }
                                    },
                                    {
                                     'type': u'ZMQSend',
                                     'fixture': {
                                            'path': 'btr'
                                     },
                                     'send_endpoint':'tcp://127.0.0.1:23000',
                                     'instance_id':'0'
                                    },
                                    {
                                     'type': u'FilePut',
                                     'fixture': {
                                            'path': 'putfile'
                                     },
                                     'remote_path':'/test'
                                    },
                                    {
                                     'type': u'FileGet',
                                     'fixture': {
                                            'path': 'getfile'
                                     },
                                     'remote_path':'/test'
                                    }
                                 )
                             },
                            )
                        },
                    'id': u'mycroft_machine_for_bpc3ui_2',
                    'desc': u'test for bpc3ui'
                }

    def setUp(self):
        self._single_xml_config = MycroftConfig(
                                    os.path.join(self.base_path, 'singlexml')
                                    )
        self._multi_xml_config = MycroftConfig(
                                    os.path.join(self.base_path, 'multixml')
                                    )
        super(ConfigTestCase, self).setUp()

    def test_load_single_config(self):
        machines = self._single_xml_config.machines
        self.assertEqual(
               [self.test_single_machine],
                machines
            )

    def test_load_multi_config(self):
        machines = self._multi_xml_config.machines
        self.assertEqual(
               [
                   self.test_multi_machine_1,
                   self.test_multi_machine_2
               ],
                machines
            )

    def test_get_machine_config(self):
        machine = self._single_xml_config.get_machine('mycroft_machine_for_bpc3ui')
        self.assertEqual(self.test_single_machine, machine)

    def tearDown(self):
        super(ConfigTestCase, self).tearDown()
