#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from .execute import ExecuteCommand
from .zmqsender import ZMQSendCommand, MultiZMQSendCommand
from .file import FilePutCommand, FileGetCommand, FileDiffCommand, FileFolderDiffCommand, FileDiffOfXMLCommand, FileDiffOfCSVCommand
from .mongo import MongoImportCommand, MongoDiffCommand, MongoDisorderDiffCommand, MongoCleanCommand
from .wait import AlerttsWaitCommand
from .postRequest import PostRequestCommand
from .transtrack import MultiTTDiffCommand, TTDiffCommand
from .api import GetApiRecordsCommand

class CommandFactory(object):

    def __init__(self, vm, **kwargs):
        self._vm = vm
        self._cmd_params = kwargs

    def gen_cmd(self):
        if self._cmd_params['type'] == 'MongoImport':
            return MongoImportCommand(self._cmd_params['ip'],
                                      self._cmd_params['fixture']['path'],
                                      self._cmd_params.get('dropfirst', True)
                                      )
        elif self._cmd_params['type'] == 'MongoDiff':
            return MongoDiffCommand(self._cmd_params['ip'],
                                    self._cmd_params['fixture']['path'],
                                    [key.strip() for key in self._cmd_params.get('exclude', '').split(',')],
                                    self._cmd_params.get('auto_format', False)
                                    )
        elif self._cmd_params['type'] == 'MongoDisorderDiff':
            return MongoDisorderDiffCommand(self._cmd_params['ip'],
                                    self._cmd_params['fixture']['path'],
                                    [key.strip() for key in self._cmd_params.get('exclude', '').split(',')],
                                    self._cmd_params.get('auto_format', False)
                                    )
        elif self._cmd_params['type'] == 'MongoClean':
            return MongoCleanCommand(self._cmd_params['ip'],
                                     self._cmd_params['fixture']['path'],
                                     )
        elif self._cmd_params['type'] == 'FilePut':
            return FilePutCommand(self._vm,
                                  self._cmd_params['fixture']['path'],
                                  self._cmd_params['remote_path']
                                  )
        elif self._cmd_params['type'] == 'FileGet':
            return FileGetCommand(self._vm,
                                  self._cmd_params['fixture']['path'],
                                  self._cmd_params['remote_path']
                                  )
        elif self._cmd_params['type'] == 'Execute':
            return ExecuteCommand(self._vm,
                                  self._cmd_params['cmd']
                                  )
        elif self._cmd_params['type'] == 'ZMQSend':
            return ZMQSendCommand(self._cmd_params['send_endpoint'],
                                  self._cmd_params['fixture']['path'],
                                  self._cmd_params['instance_id'],
                                  self._cmd_params.get('workcount',None),
                                  )
        elif self._cmd_params['type'] == 'MultiZMQSend':
            return MultiZMQSendCommand(self._cmd_params['send_endpoints']['send_endpoint'],
                                  self._cmd_params['fixture']['path'],
                                  self._cmd_params['fixture']['instance_id_path'],
                                  self._cmd_params.get('workcount',None),
                                  )
        elif self._cmd_params['type'] == 'WaitAlertts':
            return AlerttsWaitCommand(self._cmd_params['ip'],
                                       self._cmd_params['app'],
                                       self._cmd_params['ts'],
                                  )
        elif self._cmd_params['type'] == 'PostRequest':
            return PostRequestCommand(self._cmd_params['ip'],
                                       self._cmd_params.get('postip', None),
                                       self._cmd_params.get('postdata', None),
                                       self._cmd_params['posturl'],
                                       self._cmd_params.get('postthenget', False),
                                       self._cmd_params.get('rltfile_name', None),
                                       self._cmd_params.get('fixture', None),
                                  )
        elif self._cmd_params['type'] == 'MultiTTDiff':
            return MultiTTDiffCommand(self._cmd_params['ip'],
                                  self._cmd_params['fixture']['path'],
                                  self._cmd_params['transtrack']['app'],
                                  self._cmd_params['transtrack']['cap'],
                                  self._cmd_params['transtrack']['ts_start'],
                                  self._cmd_params['transtrack']['ts_end'],
                                  self._cmd_params['exclude'],
                                  )
        elif self._cmd_params['type'] == 'TTDiff':
            return TTDiffCommand(self._cmd_params['ip'],
                                  self._cmd_params['fixture']['path'],
                                  self._cmd_params['transtrack']['app'],
                                  self._cmd_params['transtrack']['cap'],
                                  self._cmd_params['transtrack']['ts_start'],
                                  self._cmd_params['transtrack']['ts_end'],
                                  self._cmd_params['exclude'],
                                  )
        elif self._cmd_params['type'] == 'FileDiff':
            return FileDiffCommand(self._vm,
                                  self._cmd_params.get('filetype', 'others'),
                                  self._cmd_params['fixture']['local_path'],
                                  self._cmd_params['fixture']['remote_path'],
                                  [key.strip() for key in self._cmd_params.get('exclude', '').split(',')],
                                  )
        elif self._cmd_params['type'] == 'FileFolderDiff':
            return FileFolderDiffCommand(
                                  self._cmd_params['fixture']['folder1_path'],
                                  self._cmd_params['fixture']['folder2_path'],
                                  )
        elif self._cmd_params['type'] == 'FileDiffOfXML':
            return FileDiffOfXMLCommand(
                                  self._cmd_params['fixture']['local_path'],
                                  self._cmd_params['fixture']['remote_path'],
                                  )
        elif self._cmd_params['type'] == 'FileDiffOfCSV':
            return FileDiffOfCSVCommand(self._vm,
                                  self._cmd_params['fixture']['local_path'],
                                  self._cmd_params['fixture']['remote_path'],
                                  )
        elif self._cmd_params['type'] == 'GetApiRecords':
            return GetApiRecordsCommand(self._cmd_params['ip'],
                                  self._cmd_params['apitype'],
                                  self._cmd_params['parameter']['app'],
                                  self._cmd_params['parameter']['cap'],
                                  self._cmd_params['parameter']['ts_start'],
                                  self._cmd_params['parameter']['ts_end'],
                                  self._cmd_params['parameter'].get('limit', None),
                                  self._cmd_params['parameter'].get('alert_type', None),
                                  self._cmd_params['parameter'].get('indicator', None),
                                  self._cmd_params['parameter'].get('sort', None),
                                  self._cmd_params['parameter'].get('status', None),
                                  [key.strip() for key in self._cmd_params['parameter'].get('dimensions', '').split(',')],
                                  [key.strip() for key in self._cmd_params['parameter'].get('fields', '').split(',')],
                                  self._cmd_params['fixture']['path'],
                                  )
        else:
            raise ValueError("No support command type {}".format(
                                                self._cmd_params['type']))
