#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
from collections import OrderedDict

from .configx.core.loader import XMLLoader
from .configx.core.generic import ReadOnlyConfig
from .configx.core.exceptions import ValidationError
from .configx.core.fields import (
    FieldName,
    StringField,
    ChoiceField,
    TimeSpanField,
    IPv4Field,
    URLField,
    PortField,
    BooleanField,
    IntegerField,
)

class Config(ReadOnlyConfig):

    endpoint = 'mycroftcase'
    loader_class = XMLLoader

    def __init__(self, base_path, file_name, **kwargs):
        self._base_path = base_path
        self._file_name = file_name
        super(Config, self).__init__(**kwargs)

    def get_file(self, **kwargs):
        return os.path.join(self._base_path, self._file_name)

    def get_loader_context(self):
        return {
                'root': self.endpoint,
                'file_path': os.path.join(self._base_path, self._file_name)
               }

class _MycroftConfig(Config):

    fields = {
        FieldName('machines', alias='machine', optional=True): [
            {
                FieldName('id', alias='@id'): StringField(),
                'ip': IPv4Field(),
                FieldName('eths', optional=True): StringField(),
                'gateway': IPv4Field(),
                'project': StringField(),
                'desc': StringField(),
                'dockerflyd': URLField(),
                FieldName('autodelete', optional=True): BooleanField(),

                FieldName('ActionGroups', alias='actionGroup', optional=True):
                    {
                        FieldName('setUp', optional=True): [
                            {
                                FieldName('commands', alias='command', optional=True): [
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['MongoImport']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['MongoDiff']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('exclude', optional=True): StringField(),
                                        FieldName('auto_format', optional=True): BooleanField()
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['MongoDisorderDiff']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('exclude', optional=True): StringField(),
                                        FieldName('auto_format', optional=True): BooleanField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['FilePut', 'FileGet']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('remote_path'): StringField()
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['Execute']),
                                        FieldName('fixture', optional=True): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('cmd'):StringField()
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['ZMQSend']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('send_endpoint', alias='endpoint'): StringField(),
                                        FieldName('instance_id'): StringField(),
                                        FieldName('workcount', optional=True): IntegerField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['MultiZMQSend']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                            FieldName('instance_id_path'): StringField(),
                                        },
                                        FieldName('send_endpoints', alias='endpoints'): {
                                            FieldName('send_endpoint', alias='endpoint'): [StringField()],
                                        },
                                        FieldName('workcount', optional=True): IntegerField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['WaitAlertts']),
                                            FieldName('app'): StringField(),
                                            FieldName('ts'): IntegerField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['PostRequest']),
                                            FieldName('postip', optional=True): StringField(),
                                            FieldName('postdata', optional=True): StringField(),
                                            FieldName('posturl'): StringField(),
                                            FieldName('postthenget', optional=True): BooleanField(),
                                            FieldName('rltfile_name', optional=True): StringField(),
                                            FieldName('fixture',optional=True): {
                                                FieldName('rltfile_path'): StringField(),
                                            },
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['MultiTTDiff']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('transtrack'): {
                                            FieldName('app'): StringField(),
                                            FieldName('cap'): StringField(),
                                            FieldName('ts_start'): StringField(),
                                            FieldName('ts_end'): StringField(),
                                        },
                                        FieldName('exclude'): StringField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['TTDiff']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                        FieldName('transtrack'): {
                                            FieldName('app'): StringField(),
                                            FieldName('cap'): StringField(),
                                            FieldName('ts_start'): StringField(),
                                            FieldName('ts_end'): StringField(),
                                        },
                                        FieldName('exclude'): StringField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['FileDiff']),
                                        FieldName('filetype', optional=True): StringField(),
                                        FieldName('fixture'): {
                                            FieldName('local_path'): StringField(),
                                            FieldName('remote_path'): StringField(),
                                        },
                                        FieldName('exclude', optional=True): StringField(),
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['FileFolderDiff']),
                                        FieldName('fixture'): {
                                            FieldName('folder1_path'): StringField(),
                                            FieldName('folder2_path'): StringField(),
                                        },
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['FileDiffOfXML']),
                                        FieldName('fixture'): {
                                            FieldName('local_path'): StringField(),
                                            FieldName('remote_path'): StringField(),
                                        },
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['FileDiffOfCSV']),
                                        FieldName('local', optional=True): BooleanField(),
                                        FieldName('fixture'): {
                                            FieldName('local_path'): StringField(),
                                            FieldName('remote_path'): StringField(),
                                        },
                                    },
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['GetApiRecords']),
                                        FieldName('apitype'): StringField(),
                                        FieldName('parameter'): {
                                            FieldName('app'): StringField(),
                                            FieldName('cap'): StringField(),
                                            FieldName('ts_start'): StringField(),
                                            FieldName('ts_end'): StringField(),
                                            FieldName('limit', optional=True): StringField(),
                                            FieldName('alert_type', optional=True): StringField(),
                                            FieldName('indicator', optional=True): StringField(),
                                            FieldName('sort', optional=True): StringField(),
                                            FieldName('status', optional=True): StringField(),
                                            FieldName('dimensions', optional=True): StringField(),
                                            FieldName('fields', optional=True): StringField(),
                                        },
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        },
                                    },
                                ],
                            }
                        ],
                        FieldName('wait', optional=True): [
                            {
                                FieldName('commands', alias='command', optional=True): [
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['WaitAlertts']),
                                            FieldName('app'): StringField(),
                                            FieldName('ts'): IntegerField(),
                                    },
                                ],
                            }
                        ],
                        FieldName('tearDown', optional=True): [
                            {
                                FieldName('commands', alias='command', optional=True): [
                                    {
                                        FieldName('type', alias='@type'): ChoiceField(choices=['MongoClean']),
                                        FieldName('fixture'): {
                                            FieldName('path'): StringField(),
                                        }
                                    },
                                ],
                            }
                        ]
                    }
            },
        ]
    }

    @property
    def machines(self):
        return self.readonly(self._data.get('machines', []))

class MycroftConfig(object):

    def __init__(self, base_path):
        self._base_path = base_path

    @property
    def configs(self):
        configs = []
        for f in os.listdir(self._base_path):
            if os.path.isdir(f):
                continue
            if f.endswith('.xml'):
                configs.append(_MycroftConfig(self._base_path, f))
        return configs

    @property
    def machines(self):
        machines = {}
        for c in self.configs:
            for vm in c.machines:
                if vm.id in machines:
                    raise ValueError("duplicate machine %s found.{}".format(vm.id))
                machines[vm.id] = vm
        return sorted(machines.values(), key=lambda x:x['id'])

    def get_machine(self, id):
        for vm in self.machines:
            if vm.id == id:
                return vm
        else:
            raise ValueError("cannot find machine.{}".format(id))
