# -*- coding: utf-8 -*-

import time
import urllib
import urlparse
from datetime import datetime

from .error import BPCRestfulAPIError, BPCRestfulAuthError
from .base import BPCRestfulAPIBase, BPCRestfulResultsBase
from .base import BPC_RESTFUL_PARAM_NONE

class Stats(BPCRestfulAPIBase):

    def __repr__(self):
        return '<BPCRestfulAPI Stats>'

    def __init__(self, auth_checker,
                 earliest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 latest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 step_limit = 100,
                 sort=[{'field': 'trans_count', 'order': 'DESC'}],
                 view_name='app1',
                 cap_name='intf1',
                 indicators=['trans_count', 'succ_rate', 'duration', 'rr_rate'],
                 dimensions=BPC_RESTFUL_PARAM_NONE,
                 stats_filter=BPC_RESTFUL_PARAM_NONE, search_timeout=30):
        """Fetches stats rows

        Args:
            earliest -- latest:  stats time scope, support ISO8601, exp:'2015-01-01T00:00:00'

            step_limit: return rows limit per request. limit should in range (0, 200])

            view_name: app1

            cap_name: intf2

            indicators: ['duration' , 'trans_count' , 'rr_rate' , 'succ_rate']

            dimensions: ['ip_src', 'ip_dst', 'ret_code', 'trans_type', 'site', ......]

            filter: {'trans_count' :{'$gte', 2000}, 'rr_rate' : {'$lt': 100}, 'succ_rate' : {'$eq': 100}, 'duration'}
        """
        super(Stats, self).__init__(auth_checker)

        self._params = {
                          'earliest': earliest,
                          'latest': latest,
                          'sort': sort,
                          'view_name': view_name,
                          'cap_name': cap_name,
                          'indicators': indicators,
                          'dimensions': dimensions,
                          'filter': stats_filter
                       }

        self._search_id = None
        self._search_status = None
        self._search_timeout = search_timeout
        self._recode_mode = True
        self._step_limit = step_limit

    def get_total_records(self):
        return self._do_request().json['items']

    def get_total_raw_records(self):
        return self._do_request()

    @property
    def search_id(self):
        """get search id
            {"sid": "d3c72b87c0bad88fa7d79d8b3c4731fc:datastat_0"}
        """
        return self._search_id

    @property
    def search_status(self):
        """search status

            exp:
            {
                "state": "209 DONE",
                "links": [
                    {
                        "href": "http://172.16.11.217/api/search/stats/73da19b596d1cb627b18790fff5dba5c:datastat_1",
                        "method": "get",
                        "rel": "self"
                    },
                    {
                        "href": "http://172.16.11.217/api/search/stats/73da19b596d1cb627b18790fff5dba5c:datastat_1",
                        "method": "delete",
                        "rel": "delete"
                    },
                    {
                        "href": "http://172.16.11.217/api/search/stats/73da19b596d1cb627b18790fff5dba5c:datastat_1/results",
                        "method": "get",
                        "rel": "results"
                    }
                ]
            }
        """

        return self._search_status

    def _do_request(self):
        """Fetches raw stats rows

        Returns:
            BPCRestfulResultsBase instance

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
        """

        stats_response = self._post('search/stats/', **self._params)
        self._search_id = BPCRestfulResultsBase(self.auth_checker, stats_response).json

        #get search status until search finished
        wait_time = 1
        while True:
            if wait_time > self._search_timeout:
                break

            self._search_status = BPCRestfulResultsBase(self.auth_checker,
                                                        self._get(stats_response.headers['location'])).json
            if self._search_status['state'] == '209 DONE':
                results_url = self._get_results_url()
                params = {'limit': self._step_limit}
                url_parts = list(urlparse.urlparse(results_url))
                query = dict(urlparse.parse_qsl(url_parts[4]))
                query.update(params)
                url_parts[4] = urllib.urlencode(query)
                return BPCRestfulResultsBase(self.auth_checker, self._get(self._get_results_url()))

            time.sleep(1)
            wait_time += 1

        raise BPCRestfulAPIError('search action Timeout')

    def _get_results_url(self):
        if self._search_status:
            link = filter(lambda x: x['rel'] == 'results', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPIError("can't get invalid results url")

    def _get_delete_url(self):
        if self._search_status:
            link = filter(lambda x: x['rel'] == 'delete', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPIError("can't get invalid delete url")

    def _get_cancel_url(self):
        if self._search_status and self._search_status['state'] != '209 DONE':
            link = filter(lambda x: x['rel'] == 'results', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPIError("can't get invalid cancel url")
