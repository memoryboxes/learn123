# -*- coding: utf-8 -*-

from simplejson.decoder import JSONDecodeError

class BPCRestfulBaseError(Exception):
    def __str__(self):
        return "***status_code:%s error_code:%s*** %s" % (self.status, self.reason, self.msg)


class BPCRestfulAuthError(BPCRestfulBaseError):
    def __init__(self, status, reason, msg={}):
        self.status = status
        self.reason = reason
        self.msg = {}


class BPCRestfulAPIError(BPCRestfulBaseError):

    def __init__(self, resp):
        self.status = resp.status_code
        try:
            self.reason = resp.json().get('error_code', resp.json())
            self.msg = resp.json().get('detail', resp.json())
        except JSONDecodeError:
            self.reason = resp.reason
            self.msg = resp.content

class BPCRestfulAPISDKError(BPCRestfulBaseError):

    def __init__(self, msg):
        self.status = 1000
        self.reason = 1000
        self.msg = msg
