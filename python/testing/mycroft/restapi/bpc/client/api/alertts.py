# -*- coding: utf-8 -*-

import time
import urllib
import urlparse
from datetime import datetime

from .error import BPCRestfulAPIError, BPCRestfulAuthError
from .base import BPCRestfulAPIBase, BPCRestfulResultsBase
from .base import BPC_RESTFUL_PARAM_NONE

class Alertts(BPCRestfulAPIBase):

    def __repr__(self):
        return '<BPCRestfulAPI Alertts>'

    def __init__(self, auth_checker,
                 view_name=BPC_RESTFUL_PARAM_NONE,
                 cap_name=BPC_RESTFUL_PARAM_NONE):
        """Fetches alertts rows

        Args:
            view_name: app1

            cap_name: intf2
        """
        super(Alertts, self).__init__(auth_checker)

        self._params = {
                          'view_name': view_name,
                          'cap_name': cap_name,
                       }

    def get_total_records(self):
        return [item for item in self.iter_records()]

    def get_total_raw_records(self):
        return [item for item in self.iter_raw_records()]

    def get_total_count(self):
        return len(self.iter_raw_records())

    def iter_records(self):
        """Fetches alertts rows

        Returns:
            items iterator

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
        """

        for group_records in self.iter_raw_records():
            for record in group_records.json.get('items', []):
                yield record

    def iter_raw_records(self):
        """Fetches raw alertts rows

        Returns:
            BPCRestfulResultsBase instance

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
        """

        return BPCRestfulResultsBase(self.auth_checker, self._get('alert_ts/', **self._params))