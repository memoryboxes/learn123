# -*- coding: utf-8 -*-

import copy
import json
import requests
from urlparse import urljoin

from .error import BPCRestfulAPIError, BPCRestfulAuthError, BPCRestfulAPISDKError

BPC_RESTFUL_PARAM_NONE = 'bpc restful not config param'

def check_execption(func):
    def _check(*arg, **kws):
        resp = func(*arg, **kws)
        if resp.status_code >= 400:
            if resp.status_code == 401:
                raise BPCRestfulAuthError(401, 'UNAUTHORIZED')
            else:
                raise BPCRestfulAPIError(resp)

        return resp
    return _check

class BPCRestfulAuth(object):

    def __init__(self, api_endpoint, api_auth_token, api_headers):
        self._api_endpoint = api_endpoint
        self._token = api_auth_token
        self._headers = api_headers
        self._headers['Authorization'] =  "token %s" % self._token
        self._headers['Cache-Control'] = 'no-cache'

    @property
    def token(self):
        return self._token

    def refresh_token(self, refresh_token):
        self._token = refresh_token
        self._headers['Authorization'] =  "token %s" % self._token
        return self._token

    @check_execption
    def get(self, url, **kws):
        return requests.get(urljoin(self._api_endpoint, url),
                            params = kws,
                            headers=self._headers)

    @check_execption
    def post(self, url, **kws):
        return requests.post(urljoin(self._api_endpoint, url),
                             data = json.dumps(kws),
                             headers=self._headers)

    @check_execption
    def put(self, url, **kws):
        return requests.put(urljoin(self._api_endpoint, url),
                            data = json.dumps(kws),
                            headers=self._headers)

    @check_execption
    def delete(self, url, **kws):
        return requests.delete(urljoin(self._api_endpoint, url),
                               data = json.dumps(kws),
                               headers=self._headers)

class BPCRestfulAPIBase(object):

    def __init__(self, auth_checker):
        self._auth_checker = auth_checker
        if not isinstance(self._auth_checker, BPCRestfulAuth):
            raise BPCRestfulAuthError(401, 'UNAUTHORIZED')

    def __repr__(self):
        return '<BPCRestfulAPI Base>'

    @property
    def auth_checker(self):
        return self._auth_checker

    def _normalize_params(self, params):
        norma_params = copy.deepcopy(params)
        for k, v in norma_params.items():
            if v == BPC_RESTFUL_PARAM_NONE:
                del norma_params[k]
        return norma_params

    def _get(self, url, **opts):
        return self._auth_checker.get(url, **self._normalize_params(opts))

    def _post(self, url, **opts):
        return self._auth_checker.post(url, **self._normalize_params(opts))

    def _put(self, url, **opts):
        return self._auth_checker.put(url, **self._normalize_params(opts))

    def _delete(self, url, **opts):
        return self._auth_checker.delete(url, **self._normalize_params(opts))

class BPCRestfulResultsBase(object):
    """pretty interface for parse json results

    args:
        resp context, exp:
        {'content': '{
            "total_count": 75,
            "items": [...],
            "limit": 1,
            "links": [
                {
                    "href": "http://172.16.11.217/api/alerts/?earliest=2015-01-22T00%3A00%3A00&limit=1&latest=2015-01-22T01%3A00%3A00",
                    "method": "get",
                    "rel": "self"
                },
                {
                    "href": "http://172.16.11.217/api/alerts/?earliest=2015-01-22T00%3A00%3A00&limit=1&offset=0&latest=2015-01-22T01%3A00%3A00",
                    "method": "get",
                    "rel": "first"
                },
                {
                    "href": "http://172.16.11.217/api/alerts/?earliest=2015-01-22T00%3A00%3A00&limit=1&offset=1&latest=2015-01-22T01%3A00%3A00",
                    "method": "get",
                    "rel": "next"
                },
                {
                    "href": "http://172.16.11.217/api/alerts/?earliest=2015-01-22T00%3A00%3A00&limit=1&offset=75&latest=2015-01-22T01%3A00%3A00",
                    "method": "get",
                    "rel": "last"
                }
            ],
            "offset": 0 }',
        'headers': '{
        }'


    """

    def __init__(self, auth_checker, results):
        self._ptr = 0
        self._auth_checker = auth_checker
        self._results = results.content
        self._json_results = json.loads(self._results)

    def __repr__(self):
        return self._results

    def __len__(self):
        if self._json_results.get('total_count', None):
            return self._json_results['total_count']
        else:
            raise BPCRestfulAPISDKError("unsupport total count fetch")

    def __iter__(self):
        return self

    def next(self):
        if self._ptr == 0:
            self._ptr += 1
            return copy.deepcopy(self)

        for link in self._json_results.get('links', []):
            if link['rel'] == 'next':
                self._results = self._auth_checker.get(link['href']).content
                self._json_results = json.loads(self._results)
                self._ptr += 1
                return copy.deepcopy(self)
        raise StopIteration

    def prev(self):
        if self._ptr == 0:
            raise StopIteration

        for link in self._json_results['links']:
            if link['rel'] == 'prev':
                self._results = self._auth_checker.get(link['href']).content
                self._json_results = json.loads(self._results)
                self._ptr -= 1
                return self
        raise StopIteration

    @property
    def json(self):
        return self._json_results

    @property
    def text(self):
        return self._results
