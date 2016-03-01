#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from .base import BaseCommand

class ExecuteCommand(BaseCommand):
    def __init__(self, vm,
                 cmd):
        self._vm = vm
        self._cmd = cmd
        super(ExecuteCommand, self).__init__(
            cmd_des="run cmd:{} in remote machine:{}".format(
                                                                self._cmd,
                                                                self._vm.ip)
        )

    def execute(self):
        return self._vm.execute(self._cmd)
