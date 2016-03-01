#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import BaseCommand
from mycroft.core.datastore.config import DBConfig, DataStore
import time


class AlerttsWaitCommand(BaseCommand):
    def __init__(self, hostip,
                 app,
                 ts):
        self._db = DataStore(DBConfig(hostip)).conn
        self._query = {}
        self._query["app"]= app
        self._query["intf"]=None
        self._query["ts"]=ts
        super(AlerttsWaitCommand, self).__init__(
            cmd_des="waiting for bpc server process(switch->worker->exporter->mongo) complete..."
        )

    def execute(self):
        count = 0
        while 1:
            if self._db['bpc']['alert_ts'].find(self._query).count() == 1 or count > 600:
                break
            else:
                time.sleep(1)
                count += 1