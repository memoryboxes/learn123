# -*- coding: utf-8 -*-

from .api import BPCRestfulAPI
from .api.base import BPCRestfulAuth

DEFAULT_RESTFULAPI_ENDPOINT = 'http://127.0.0.1/api/'
DEFAULT_RESTFULAPI_TOKEN = 'et44bf919hc62bja9488lq846dp0e4bbgfc6ff4b'
DEFAULT_RESTFULAPI_HEADERS = {
                                'Accept': 'application/vnd.crossflow.bpc+json; indent=4',
                                'Content-Type': 'application/json',
                                'Authorization': "token %s" % DEFAULT_RESTFULAPI_TOKEN,
                             }

class BPCRestfulClient(BPCRestfulAPI):

    def __init__(self,
                 api_endpoint = DEFAULT_RESTFULAPI_ENDPOINT,
                 api_auth_token = DEFAULT_RESTFULAPI_TOKEN,
                 api_headers = DEFAULT_RESTFULAPI_HEADERS):

        self.auth_checker = BPCRestfulAuth(api_endpoint, api_auth_token, api_headers)

    def __repr__(self):
        return '<BPCClient Auth client>'

    @property
    def token_code(self):
        return self.auth_checker.token

    def refresh_token(self, refresh_token):
        self.auth_checker.refresh_token(refresh_token)
        return self.auth_checker.token

