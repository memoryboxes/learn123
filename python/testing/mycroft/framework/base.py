#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import sys
import copy
import traceback
from collections import OrderedDict
from unittest import TestCase
from os.path import abspath, join, dirname, exists

from mycroft.core.client.machine import VMachine, VMStatus
from mycroft.core.client.errors import ContainerException, ContainerStatusException
from mycroft.core.datastore.errors import AssertionTextDiffError, AssertionJsonDiffError
from mycroft.configs.config import MycroftConfig
from mycroft.utils.diff.difflib import XDiff
from mycroft.framework.command.factory import CommandFactory

class BaseTestCase(TestCase):
    """ baseclass for integration testcase

    by inherit BaseTestCase, it'll do:

        * auto parse etc/*.xml to get commands during setUp or tearDown...

        * auto create vitual machines

        * import btrs

        * import mongodb

        * construct diff commands object
    """

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.base_path = abspath(dirname(sys.modules[self.__module__].__file__))
        self._config = MycroftConfig(join(self.base_path, 'etc'))
        self._vms_info = self._config.machines

        #create container vitual vms
        self._vms = self._gen_vms(self._vms_info)

        #create commands
        try:
            self._cmds = self._gen_cmds(self._vms_info)
        except Exception, e:
            print e.message
            print traceback.format_exc()
            self._cmds = {}
            self._delete_vms()

    @property
    def allcmds(self):
        """get all commands by parsing xml"""
        allcmds = []
        for vm_methods in self._cmds.values():
            for method, cmds in vm_methods.iteritems():
                allcmds.extend(cmds)

        return allcmds

    @property
    def allvms(self):
        """get all virtual machines by parsing xml, default sorted by name"""
        return self._vms

    def get_vm(self, name):
        """get assigned virtual machines by name"""
        for vm in self._vms:
            if vm.name == name:
                return vm
        return None

    def get_cmds_by_type(self, cmd_class):
        """get cmds by base class

        Args:
            cmd_class: such as MongoDiffCommand ...
        """
        return [cmd for cmd in self.allcmds if isinstance(cmd, cmd_class)]

    def get_cmds_by_method(self, method_name):
        """get cmds by base method_name

        Args:
            method_name: such as tearDown or setUp...
        """
        method_cmds = []
        for vm_methods in self._cmds.values():
            for method, cmds in vm_methods.iteritems():
                if method == method_name:
                    method_cmds.extend(cmds)
        return method_cmds

    def assertTextEqual(self, textA, textB):
        diff = XDiff().text_to_text(textA, textB).pretty_diff_console()
        if diff:
            print diff
            raise AssertionTextDiffError()

    def assertJsonEqual(self, jsonA, jsonB):
        diff = XDiff().json_to_json(jsonA, jsonB).pretty_diff_console()
        if diff:
            print diff
            raise AssertionJsonDiffError()

    def assertJsonFileEqual(self, jsonfileA, jsonfileB):
        diff = XDiff().jsonfile_to_jsonfile(jsonfileA, jsonfileB).pretty_diff_console()
        if diff:
            print diff
            raise AssertionJsonDiffError()

    def _gen_vms(self, vms_info):
        vms = []
        for vm in vms_info:
            vm_info = {
                        'name': vm['id'],
                        'ip': vm['ip'] + '/24',
                        'eths': vm.get('eths', ''),
                        'project': vm['project'],
                        'desc': vm['desc'],
                        'gateway': vm['gateway'],
                        'dockerflyd_server': vm['dockerflyd']
                      }

            vms.append(VMachine(**vm_info))

        for vm in vms:
            try:
                if vm.status == VMStatus.NOPRESENT:
                    vm.create()
            except ContainerException as e:
                print e
        return vms

    def _delete_vms(self):
        for vm in self._vms:
            if self._config.get_machine(vm.name)['autodelete']:
                vm.delete()

    def _gen_cmds(self, vms_info):
        """ gen setUp and tearDown ... commands

        Args: vms_info
                ...
                'ActionGroups': {
                    'tearDown': (
                        {'commands': (
                            {'type': u'MongoClean', 'fixture': {u'path':'importdb'},)},),
                      'setUp': (
                        {
                            'commands': (
                                {'type': u'MongoImport', 'fixture': {'path':'importdb'}},
                                {'type': u'MongoDiff', 'fixture': {'path':'diffdb'}},
                                {
                                 'type': u'ZMQSend', 'fixture': {'path':'btr'},
                                 'send_endpoint':'tcp://127.0.0.1:23000',
                                 'instance_id':'0'
                                }
                             )
                         },
                        )
                    },
                }
                ...

        return {
                    vm_id: {
                        'setUp':[cmds...],
                        'tearDown':[cmds...]
                        ...
                        },
                    ...
               }
        """
        cmds = {}
        for vm in vms_info:
            cmds[vm['id']] = {}

            #move setUp command front
            action_groups = OrderedDict()
            methods = vm['ActionGroups'].keys()
            methods.insert(0, methods.pop(methods.index('setUp')))
            for method in methods:
                action_groups[method] = vm['ActionGroups'][method]

            #generate commands and execute setUp commands
            for k, v in action_groups.iteritems():
                cmds[vm['id']][k] = []
                for cmd in v[0].get('commands', []):
                    cmd = copy.deepcopy(cmd)
                    cmd['ip'] = vm['ip']

                    for key, value in cmd.get('fixture', {}).iteritems():
                        cmd['fixture'][key] = abspath(join(self.base_path, value))

                        if not exists(cmd['fixture'][key]):
                            raise SystemError("{} does not exist".format(cmd['fixture'][key]))

                    gen_cmd = CommandFactory(self.get_vm(vm['id']), **cmd).gen_cmd()
                    cmds[vm['id']][k].append(gen_cmd)
                    if k == 'setUp':
                        gen_cmd.execute()
        return cmds


    def tearDown(self):
        for cmd in self.get_cmds_by_method('tearDown'):
            cmd.execute()

        try:
            self._delete_vms()
        except ContainerStatusException:
            pass

        super(BaseTestCase, self).tearDown()
