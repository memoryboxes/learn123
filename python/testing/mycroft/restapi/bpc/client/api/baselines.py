# -*- coding: utf-8 -*-

from datetime import datetime

from .base import BPCRestfulAPIBase, BPCRestfulResultsBase
from .base import BPC_RESTFUL_PARAM_NONE

class Baselines(BPCRestfulAPIBase):

    def __repr__(self):
        return '<BPCRestfulAPI Baselines>'

    def __init__(self, auth_checker,
                 earliest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 latest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 view_name=BPC_RESTFUL_PARAM_NONE,
                 cap_name=BPC_RESTFUL_PARAM_NONE):
        """Fetches baselines rows

        Args:
            earliest -- latest:  baselines time scope, support ISO8601, exp:'2015-01-01T00:00:00'

            view_name: app1

            cap_name: intf2
        """
        super(Baselines, self).__init__(auth_checker)

        self._params = {
                          'earliest': earliest,
                          'latest': latest,
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
        """Fetches baselines rows

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
        """Fetches raw baselines rows

        Returns:
            BPCRestfulResultsBase instance

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
        """

        return BPCRestfulResultsBase(self.auth_checker, self._get('baselines/', **self._params))
