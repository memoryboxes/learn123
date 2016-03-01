#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from unittest import main, TestCase

from mycroft.core.client.machine import VMachine, VMStatus
from mycroft.core.client.errors import ContainerStatusException
from mycroft.settings import TEST_VM_HOST

class VMsTestCase(TestCase):

    def setUp(self):
        super(VMsTestCase, self).setUp()
        self.created_vmlist = []
        self._record_mode = False

    def test_create(self):
        vm = self._get_new_vm()
        vm.create()
        self.assertEqual(vm.status, VMStatus.RUNNING)
        self.created_vmlist.append(vm)

    def test_stop_and_start(self):
        vm = self._get_new_vm()
        vm.create()
        self.created_vmlist.append(vm)
        vm.stop()
        self.assertEqual(vm.status, VMStatus.STOPPED)
        vm.start()
        self.assertEqual(vm.status, VMStatus.RUNNING)

    def test_check_status(self):
        vm = self._get_new_vm()
        vm.create()
        self.created_vmlist.append(vm)
        vm.stop()
        self.assertEqual(vm.status, VMStatus.STOPPED)
        self.assertRaises(ContainerStatusException, vm.execute, '/sbin/ifconfig')

    def test_recreate(self):
        vm = self._get_new_vm()
        vm.create()
        self.created_vmlist.append(vm)
        old_id = vm.id
        print old_id

        vm.recreate()
        new_id= vm.id
        print new_id
        self.assertNotEqual(old_id, new_id)

    def test_none_recreate(self):
        vm = self._get_new_vm()
        self.assertEqual(vm.status, VMStatus.NOPRESENT)
        vm.recreate()
        self.assertEqual(vm.status, VMStatus.RUNNING)
        self.created_vmlist.append(vm)

    def tearDown(self):
        for vm in self.created_vmlist:
            try:
                vm.delete()
            except ContainerStatusException:
                pass

        super(VMsTestCase, self).tearDown()

    def _get_new_vm(self):
        return VMachine(**TEST_VM_HOST)

if __name__ == '__main__':
    main()
