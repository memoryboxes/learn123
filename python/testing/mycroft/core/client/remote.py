#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from fabric.api import env
from fabric.api import run, get, put
from fabric.network import disconnect_all

class RemoteEnv(object):

    def __init__(self, host, user, password):
        self._host = host
        self._user = user
        self._password = password

    @property
    def host(self):
        return self._host

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

class RemoteTask(object):

    def __init__(self, remote_env):
        self._env = remote_env

        env.host_string = "{}@{}".format(remote_env.user, remote_env._host)
        env.user = remote_env._user
        env.password = remote_env._password
        env.disable_known_hosts = True
        env.eagerly_disconnect = True
        env.connection_attempts = 5

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        disconnect_all()

    def execute(self):
        raise NotImplementedError

class PutFileToRemoteTask(RemoteTask):

    def __init__(self, remote_env, local_path, remote_path):
        super(PutFileToRemoteTask, self).__init__(remote_env)
        self._local_path = local_path
        self._remote_path = remote_path

    def execute(self):
        return put(self._local_path, self._remote_path)

class GetFileFromRemoteTask(RemoteTask):

    def __init__(self, remote_env, remote_path, local_path):
        super(GetFileFromRemoteTask, self).__init__(remote_env)
        self._local_path = local_path
        self._remote_path = remote_path

    def execute(self):
        return get(self._remote_path, self._local_path)

class RunInRemoteTask(RemoteTask):

    def __init__(self, remote_env, cmdline):
        super(RunInRemoteTask, self).__init__(remote_env)
        self._cmdline = cmdline

    def execute(self):
        return run(self._cmdline)

class CheckFileExistsRemoteTask(RemoteTask):
    def __init__(self, remote_env, remote_path):
        super(CheckFileExistsRemoteTask, self).__init__(remote_env)
        self._remote_path = remote_path

    def execute(self):
        return run("[[ ! -e '{}' ]] || printf yes".format(self._remote_path)) == "yes"

class DelFileFromRemoteTask(RemoteTask):

    def __init__(self, remote_env, remote_path):
        super(DelFileFromRemoteTask, self).__init__(remote_env)
        self._remote_path = remote_path

    def execute(self):
        if CheckFileExistsRemoteTask(self._env, self._remote_path).execute():
            run ("rm -rf {}".format(self._remote_path))
