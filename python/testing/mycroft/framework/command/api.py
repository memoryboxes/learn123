#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import json
import os
from .base import BaseCommand
from mycroft.restapi.bpc.client import BPCRestfulClient


class GetApiRecordsCommand(BaseCommand):

    def __init__(self, hostip, apitype, app, cap, ts_start, ts_end, limit, alert_type, indicator, sort, status, dimensions, fields, path):
        self._hostip = hostip
        self._apitype = apitype
        self._app = app
        self._cap = cap
        self._path = path
        self._ts_start = ts_start
        self._ts_end = ts_end
        self._limit = limit
        self._alert_type = alert_type
        self._indicator = indicator
        self._sort = sort
        self._status = status
        self._dimensions = dimensions
        self._fields = fields
        self._client = BPCRestfulClient(api_endpoint='http://%s/api/' % self._hostip)
        self._apitypes = {
                        "alerts":self._get_alerts,
                        "stats":self._get_stats,
                        "baselines":self._get_baselines,
                        "trans":self._get_trans,
                        "multi_trans":self._get_multi_trans,
                        "iter_trans":self._get_iter_trans_record,
                        "iter_raw_trans":self._get_iter_raw_trans_record
                        }
        super(GetApiRecordsCommand, self).__init__(
            cmd_des='get %s record of %s:%s from %s to %s' % (self._apitype, self._app, self._cap, self._ts_start, self._ts_end))

    def execute(self):
        records = self._apitypes[self._apitype]()
        fp = open(os.path.join(self._path, '%s.json' % self._apitype),'w+')
        fp.write(json.dumps(records, ensure_ascii=False, indent=4).encode('UTF-8'))
        fp.close()

    def _get_alerts(self):
        return self._client.alerts(earliest=self._ts_start,
                                  latest=self._ts_end,
                                  view_name=self._app,
                                  cap_name=self._cap,
                                  alert_type=self._alert_type,
                                  indicator=self._indicator,
                                  sort=self._sort,
                                  status=self._status).get_total_records()

    def _get_stats(self):
        return self._client.stats(earliest=self._ts_start,
                                 latest=self._ts_end,
                                  view_name=self._app,
                                  cap_name=self._cap,
                                  dimensions=self._dimensions).get_total_records()

    def _get_baselines(self):
        return self._client.baselines(earliest=self._ts_start,
                                      latest=self._ts_end,
                                      view_name=self._app,
                                      cap_name=self._cap).get_total_records()

    def _get_trans(self):
        return self._client.trans(earliest=self._ts_start,
                                  latest=self._ts_end,
                                  view_name=self._app,
                                  cap_name=self._cap,
                                  fields=self._fields).get_total_records()

    def _get_multi_trans(self):
        return self._client.multi_trans(earliest=self._ts_start,
                                      latest=self._ts_end,
                                      view_name=self._app,
                                      cap_name=self._cap).get_total_records()

    def _get_iter_trans_record(self):
        trans_records = self._client.trans(earliest=self._ts_start,
                                  latest=self._ts_end,
                                  view_name=self._app,
                                  cap_name=self._cap).iter_records()
        records = []
        for record in trans_records:
            json.dumps(record, ensure_ascii=False, indent=4)
            records.append(record)
        return records

    def _get_iter_raw_trans_record(self):
        trans_records = self._client.trans(earliest=self._ts_start,
                                  latest=self._ts_end,
                                  view_name=self._app,
                                  cap_name=self._cap).iter_raw_records()
        records = {}
        for record in trans_records:
            records['links'] = record.json.get('links',[])
            records['items'] = record.json.get('items',[])
        return records
