#!/usr/bin/env python
#  -*- coding: utf-8 -*-

class MsgParser(object):

    def __init__(self):
        pass

    def make_header(self):
        raise NotImplementedError

    def parse(self, msgtype='msgpack'):
        raise NotImplementedError