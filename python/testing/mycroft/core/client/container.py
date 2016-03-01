#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import time
import json
import requests
import random

from mycroft.settings import IMAGE_NAME_MAP
from .errors import (RequestException,
                    ContainerException,
                    NoCreatedContainerException)

def check_execption(func):
    def _check(*arg, **kws):
        resp = func(*arg, **kws)
        if not resp or resp.status_code >= 400:
            raise ContainerException(resp.json())

        return resp
    return _check

class ContainerList(object):

    def __init__(self, dockerflyd_server):
        self._dockerflyd_server = dockerflyd_server

    @check_execption
    def get(self):
        return requests.get(self._dockerflyd_server + 'containers')

    @check_execption
    def create(self, create_containers_json):
        headers = {'content-type': 'application/json'}
        resp = requests.post(self._dockerflyd_server + 'containers',
                             data=json.dumps(create_containers_json),
                             headers=headers)
        return resp

class Container(object):

    image_name_map = IMAGE_NAME_MAP

    def __init__(self, name, ip,
                       gateway,
                       eths='',
                       project='centos6',
                       desc="mycroft testcase",
                       dockerflyd_server='http://127.0.0.1:5123/v1/'):
        """ setup all params of a container
        """
        self._dockerflyd_server = dockerflyd_server

        self._post_json = \
              {
                "gateway": "172.16.13.1",
                "eths": [
                      [
                        "mycroftv0",
                        "eth1",
                        "172.16.13.100/24"
                      ]
                    ],

                "image_name": "docker-registry.dev.netis.com.cn:5000/crossflow/centos6",
                "run_cmd": "/usr/bin/svscan /etc/dockerservices",
                "id": None,
                "pid": None,
                "status": "running",
                "container_name": "mycroft_testcase",
                "last_modify_time": 0,
                "desc": "mycroft testcase"
              }
        veth_name = "v%.6f" % time.time()
        veth_name = veth_name.replace('.', '')
        veth_name = ''.join(veth_name[6:])
        self._post_json['container_name'] = name
        self._post_json['gateway'] = gateway
        self._post_json['image_name'] = self.image_name_map[project]
        self._post_json['eths'] = [(veth_name, "eth1", ip)]
        for eth in eths.split(','):
            if eth:
                self._post_json['eths'].append([eth, "eth1", '0.0.0.0'])

    @check_execption
    def create(self):
        if self.status == 'nopresent':
            resp = ContainerList(self._dockerflyd_server).create([self._post_json])
            return resp

    @check_execption
    def start(self):
        if self.status == 'stopped':
            return requests.put(self._dockerflyd_server + 'container/' + self.id + '/active')

    @check_execption
    def stop(self):
        if self.status == 'running':
            return requests.put(self._dockerflyd_server + 'container/' + self.id + '/inactive')

    @check_execption
    def delete(self):
        return requests.delete(self._dockerflyd_server + 'container/' + self.id)

    @property
    def status(self):
        """
            return 'stopped' or 'running' or 'nopresent'
        """
        all_containers = ContainerList(self._dockerflyd_server).get().json()
        for container in all_containers:
            if self._post_json['container_name'] == container['container_name']:
                return container['status']
        return 'nopresent'

    @property
    def id(self):
        all_containers = ContainerList(self._dockerflyd_server).get().json()
        for container in all_containers:
            if self._post_json['container_name'] == container['container_name']:
                return container['id']
        raise NoCreatedContainerException()

    @classmethod
    @check_execption
    def get_inst_by_name(cls, dockerflyd_server, container_name):

        def get_project(image_name):
            for project, image_name in cls.image_name_map.iteritems():
                if image_name == container['image_name']:
                    return project
            return None

        all_containers = ContainerList(dockerflyd_server).get().json()
        for container in all_containers:
            if container_name == container['container_name']:
                project = get_project(container['image_name'])
                container_inst = Container(name=container['container_name'],
                                 ip=container['eths'][0][2],
                                 gateway=container['gateway'],
                                 project=project,
                                 desc=container['desc'],
                                 dockerflyd_server=dockerflyd_server)
                container_inst.id = container['id']
                return container_inst
        return None

