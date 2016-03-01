#!/usr/bin/env python
#  -*- coding: utf-8 -*-

class BaseCommand(object):

    def __init__(self, cmd_des="base command"):
        self._cmd_des = cmd_des
        print '\n'
        print "[mycroft command] %s" % cmd_des

    def execute(self):
        raise NotImplementedError

class DiffCommand(BaseCommand):

    def __init__(self, cmd_des="diff command"):
        super(DiffCommand, self).__init__(cmd_des)
