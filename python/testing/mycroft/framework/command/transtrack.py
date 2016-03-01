'''
Created on Jul 30, 2015

@author: evajiang
'''
import os
import json
from .base import BaseCommand
from .file import FileGetCommand
from mycroft.restapi.bpc.client import BPCRestfulClient
from mycroft.utils.diff.difflib import XDiff
from mycroft.core.datastore.errors import AssertionJsonDiffError

class MultiTTDiffCommand(BaseCommand):

    def __init__(self, hostip, path, app, cap, ts_start, ts_end, exclude):
        self._hostip = hostip
        self._app = app
        self._cap = cap
        self._path = path
        self._ts_start = ts_start
        self._ts_end = ts_end
        self._exclude = exclude.split(',')
        super(MultiTTDiffCommand, self).__init__(
            cmd_des='get multi trans record of %s:%s from %s to %s' % (self._app, self._cap, self._ts_start, self._ts_end))

    def execute(self):
        self.assertDiff(self._get_multi_trans())

    def assertDiff(self, remote):
        local = [self._stripkey(record, self._exclude) for record in json.load(open(os.path.join(self._path, '%s_%s.json' % (self._cap, self._timeformat(self._ts_start))), 'r'))]
        remote = [self._stripkey(record, self._exclude) for record in remote]
        json.dumps(remote, os.path.join(self._path, '%s_%s.json' % (self._cap, self._timeformat(self._ts_start))))
        diff = XDiff().json_to_json(self._stripkey(local, self._exclude), self._stripkey(remote, self._exclude)).pretty_diff_console()
        if diff:
            print diff
            raise AssertionJsonDiffError()

    def _stripkey(self, json_obj, keys):
        if not isinstance(json_obj, dict):
            return json_obj

        for key in keys:
            if json_obj.get(key, None) != None:
                del json_obj[key]
        for key, value in json_obj.iteritems():
            if isinstance(value, dict):
                self._stripkey(value, keys)
            elif isinstance(value, list):
                for item in value:
                    self._stripkey(item, keys)
        return json_obj

    def _timeformat(self, ts):
        return ts.replace('-', '').replace('T', '').replace(':', '')

    def _get_multi_trans(self):
        client = BPCRestfulClient(api_endpoint='http://%s/api/' % self._hostip)
        return client.multi_trans(earliest=self._ts_start,
                                  latest=self._ts_end,
                                  view_name=self._app,
                                  cap_name=self._cap).get_total_records()

class TTDiffCommand(BaseCommand):

    def __init__(self, hostip, path, app, cap, ts_start, ts_end, exclude):
        self._hostip = hostip
        self._app = app
        self._cap = cap
        self._path = path
        self._ts_start = ts_start
        self._ts_end = ts_end
        self._exclude = exclude.split(',')
        super(TTDiffCommand, self).__init__(
            cmd_des='get trans record of %s:%s from %s to %s' % (self._app, self._cap, self._ts_start, self._ts_end))

    def execute(self):
        self.assertDiff(self._get_trans())

    def assertDiff(self, remote):
        local = [self._stripkey(record, self._exclude) for record in json.load(open(os.path.join(self._path, '%s_%s.json' % (self._cap, self._timeformat(self._ts_start))), 'r'))]
        remote = [self._stripkey(record, self._exclude) for record in remote]
        diff = XDiff().json_to_json(self._stripkey(local, self._exclude), self._stripkey(remote, self._exclude)).pretty_diff_console()
        if diff:
            print diff
            raise AssertionJsonDiffError()

    def _stripkey(self, json_obj, keys):
        if not isinstance(json_obj, dict):
            return json_obj

        for key in keys:
            if json_obj.get(key, None) != None:
                del json_obj[key]
        for key, value in json_obj.iteritems():
            if isinstance(value, dict):
                self._stripkey(value, keys)
            elif isinstance(value, list):
                for item in value:
                    self._stripkey(item, keys)
        return json_obj

    def _timeformat(self, ts):
        return ts.replace('-', '').replace('T', '').replace(':', '')

    def _get_trans(self):
        client = BPCRestfulClient(api_endpoint='http://%s/api/' % self._hostip)
        return client.trans(earliest=self._ts_start,
                            latest=self._ts_end,
                            view_name=self._app,
                            cap_name=self._cap).get_total_records()
