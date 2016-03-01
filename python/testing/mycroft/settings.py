#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from datetime import date
from os.path import abspath, dirname

BPC_PATH = '/opt/bpc'
NPMDATA_PATH = '/opt/npm'
NPMWEB_PATH = '/opt/npmweb'
SMARTPROBE_PATH = '/opt/smartprobe/sp'

RC_HOST = "172.16.11.80"
RC_PORT = 2222

PROJECT_ROOT = abspath(dirname(__file__))

# green whale 172.16.14.22 可用
# blue whale 172.16.11.181

TEST_VM_HOST = {'name':'test_create_vm1_for_mycroft_own',
                'ip':'172.16.13.31/24',
                'project':'bpc3',
                'desc':'unit test for mycroft',
                'gateway':'172.16.13.1',
                'dockerflyd_server':'http://172.16.11.13:5123/v1/'
                }

TEST_ETH_HOST = {'name':'test_create_vm2_for_mycroft_own',
                'ip':'172.16.13.31/24',
                'eths':'eth_test',
                'project':'bpc3',
                'desc':'unit test for mycroft',
                'gateway':'172.16.13.1',
                'dockerflyd_server':'http://172.16.11.13:5123/v1/'
                }

BASE_DOCKER_REPO = "docker-registry.dev.netis.com.cn:5000/autobuild/"
DATE_TAG = date.today().strftime("%Y%m%d")
IMAGE_NAME_MAP = {
            'centos6':BASE_DOCKER_REPO + 'centos6',
            'bpc3':BASE_DOCKER_REPO + 'bpc3_source_anonymous_snapshot:' + DATE_TAG,
            'npm3':BASE_DOCKER_REPO + 'npm3_source_anonymous_snapshot:' + DATE_TAG,
            'smartprobe':BASE_DOCKER_REPO + 'smartprobe_source_anonymous_snapshot:' + DATE_TAG,
            'webservice_syslog':'docker-registry.dev.netis.com.cn:5000/crossflow/webservice_syslog:latest',
        }

try:
    from local_settings import *
except ImportError:
    pass
