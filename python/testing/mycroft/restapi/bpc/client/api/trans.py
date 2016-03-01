# -*- coding: utf-8 -*-

import time
import urllib
import urlparse
from datetime import datetime

from .error import BPCRestfulAPIError, BPCRestfulAuthError, BPCRestfulAPISDKError
from .base import BPCRestfulAPIBase, BPCRestfulResultsBase
from .base import BPC_RESTFUL_PARAM_NONE

class Trans(BPCRestfulAPIBase):

    def __repr__(self):
        return '<BPCRestfulAPI Trans>'

    def __init__(self, auth_checker,
                 earliest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 latest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 step_limit = 100,
                 sort=[{'field': 'trans_count', 'order': 'DESC'}],
                 view_name='app1',
                 cap_name=BPC_RESTFUL_PARAM_NONE,
                 fields=BPC_RESTFUL_PARAM_NONE,
                 trans_filter=BPC_RESTFUL_PARAM_NONE,
                 search_timeout=30):
        """Fetches trans rows

        Args:
            earliest -- latest:  trans time scope, support ISO8601, exp:'2015-01-01T00:00:00'

            step_limit: return rows limit per request. limit should in range (0, 200])

            view_name: app1

            cap_name: intf2

            fields: ['ts', 'duration', 'ret_code', 'ip_src', 'ip_dst', 'trans_type', 'serial_number', 'your own dimension field']

            trans_filter: {"ret_code" : '05', "ip_dst" : '144.7.28.14'}
        """
        super(Trans, self).__init__(auth_checker)

        self._params = {
                          'earliest': earliest,
                          'latest': latest,
                          'sort': sort,
                          'view_name': view_name,
                          'cap_name': cap_name,
                          'fields': fields,
                          'filter': trans_filter,
                       }

        self._step_limit = step_limit
        self._search_id = None
        self._search_status = None
        self._search_timeout = search_timeout
        self._search_url = 'search/trans/'

    def get_total_records(self):
        return [item for item in self.iter_records()]

    def get_total_raw_records(self):
        return [item for item in self.iter_raw_records()]

    def get_total_count(self):
        return len(self.iter_raw_records())

    def iter_records(self):
        """Fetches trans rows

        Returns:
            record iterator

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
            BPCRestfulAPISDKError: An error occurred by sdk framework
        """

        for group_records in self.iter_raw_records():
            for record in group_records.json.get('items', []):
                yield record

    def iter_raw_records(self):
        """Fetches raw trans rows

        Returns:
            BPCRestfulResultsBase instance

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
            BPCRestfulAPISDKError: An error occurred by sdk framework
        """

        return self._do_request()

    def delete_search(self):
        self._delete(self._get_delete_url())

    def cancel_search(self):
        self._cancel(self._get_cancel_url())

    @property
    def search_id(self):
        """get search id
            {"sid":"1421307606.01"}
        """
        return self._search_id

    @property
    def search_status(self):
        """search status

            exp:
                {
                    "progress": 100,
                    "state": "209 DONE",
                    "links": [
                        {
                            "href": "http://127.0.0.1/api/search/trans/1421307606.01",
                            "method": "get",
                            "rel": "self"
                        },
                        {
                            "href": "http://127.0.0.1/api/search/trans/1421307606.01",
                            "method": "delete",
                            "rel": "delete"
                        },
                        {
                            "href": "http://127.0.0.1/api/search/trans/1421307606.01/preview",
                            "method": "get",
                            "rel": "preview"
                        },
                        {
                            "href": "http://127.0.0.1/api/search/trans/1421307606.01/results",
                            "method": "get",
                            "rel": "results"
                        }
                    ],
                    "avail_count": 160
                }
        """

        return BPCRestfulResultsBase(self.auth_checker,
                                     self._get(self._search_url+self._search_id['sid'])).json

    def _do_request(self):
        """Fetches raw trans rows

        Returns:
            BPCRestfulResultsBase instance

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
            BPCRestfulAPISDKError: An error occurred by sdk framework
        """

        trans_response = self._post(self._search_url, **self._params)
        self._search_id = BPCRestfulResultsBase(self.auth_checker, trans_response).json

        #get search status until search finished
        wait_time = 1
        while True:
            if wait_time > self._search_timeout:
                break

            self._search_status = BPCRestfulResultsBase(self.auth_checker,
                                                        self._get(trans_response.headers['location'])).json
            if self._search_status['state'] == '209 DONE':
                results_url = self._get_results_url()
                params = {'limit': self._step_limit}
                url_parts = list(urlparse.urlparse(results_url))
                query = dict(urlparse.parse_qsl(url_parts[4]))
                query.update(params)
                url_parts[4] = urllib.urlencode(query)
                return BPCRestfulResultsBase(self.auth_checker, self._get(urlparse.urlunparse(url_parts)))

            time.sleep(1)
            wait_time += 1

        raise BPCRestfulAPISDKError('search action Timeout')

    def _get_results_url(self):
        if self._search_status:
            link = filter(lambda x: x['rel'] == 'results', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPISDKError("can't get invalid results url")

    def _get_preview_url(self):
        if self._search_status:
            link = filter(lambda x: x['rel'] == 'preview', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPISDKError("can't get invalid results url")

    def _get_delete_url(self):
        if self._search_status:
            link = filter(lambda x: x['rel'] == 'delete', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPISDKError("can't get invalid delete url")

    def _get_cancel_url(self):
        if self._search_status and self._search_status['state'] != '209 DONE':
            link = filter(lambda x: x['rel'] == 'results', self._search_status['links'])

            if link and link[0].get('href', None):
                return link[0]['href']

            raise BPCRestfulAPISDKError("can't get invalid cancel url")


class MultiTrans(Trans):
    def __init__(self, auth_checker,
                 earliest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 latest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 step_limit = 100,
                 sort=[{'field': 'trans_count', 'order': 'DESC'}],
                 view_name='app1',
                 cap_name='cap1',
                 fields=BPC_RESTFUL_PARAM_NONE,
                 trans_filter=BPC_RESTFUL_PARAM_NONE,
                 link_fields={},
                 search_timeout=30):
        """Fetches multi trans rows

        Args:
            earliest -- latest:  trans time scope, support ISO8601, exp:'2015-01-01T00:00:00'

            step_limit: return rows limit per request. limit should in range (0, 1000])

            view_name: app1

            cap_name: cap1

            path: path name, in /opt/bpc/etc/apps/transtrack.xml

            fields: ['ts', 'duration', 'ret_code', 'ip_src', 'ip_dst', 'trans_type', 'your own dimension field']

            filter: {"ret_code" : '05', "ip_dst" : '144.7.28.14'}
        """
        super(MultiTrans, self).__init__(auth_checker,
                                         earliest=earliest,
                                         latest=latest,
                                         step_limit = step_limit,
                                         sort=sort,
                                         view_name=view_name,
                                         cap_name=cap_name,
                                         fields = fields,
                                         trans_filter=trans_filter,
                                         search_timeout=search_timeout)
        self._params['is_multitier'] = True
        if link_fields:
            self._params['link_fields'] = link_fields

        self._search_url = 'search/trans/'

