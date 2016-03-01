import logging
import xmlrpclib

logger = logging.getLogger('default')

class RPCServerError(Exception):
    pass

class ProcessInfo(object):

    def __init__(self, info):
        self.__info = info

    def __getattr__(self, name):
        try:
            return getattr(self.__info, name)
        except:
            return None

    @property
    def name(self):
        return self.get('name')

    @property
    def group(self):
        return self.get('group')

    @property
    def start(self):
        return self.get('start')

    @property
    def stop(self):
        return self.get('stop')

    @property
    def now(self):
        return self.get('now')

    @property
    def state(self):
        return self.get('state')

    @property
    def statename(self):
        return self.get('statename')

    @property
    def stdout_logfile(self):
        return self.get('stdout_logfile')

    @property
    def stderr_logfile(self):
        return self.get('stderr_logfile')

    @property
    def spawnerr(self):
        return self.get('spawnerr')

    @property
    def exitstatus(self):
        return self.get('exitstatus')

    @property
    def pid(self):
        return self.get('pid')



class SupervisorRpcClient(object):

    def __init__(self, host='127.0.0.1', port=9001):
        self.__host = host
        self.__port = port
        self.__server = self.__gen_server().supervisor

    def __gen_server(self):
        try:
            return xmlrpclib.ServerProxy('http://%(host)s:%(port)s/RPC2' % {'host': self.__host, 'port': self.__port})
        except:
            logger.error('get supervisor rpc server fail')
            raise RPCServerError()

    def process(self, process_name):
        try:
            return ProcessInfo(self.__server.getProcessInfo(process_name))
        except Exception, e:
            raise RPCServerError(e.message)

    def all_process(self):
        try:
            return [ProcessInfo(info) for info in self.__server.getAllProcessInfo()]
        except Exception, e:
            raise RPCServerError(e.message)

    def start(self, process_name, wait=True):
        try:
            return self.__server.startProcess(process_name, wait)
        except Exception, e:
            raise RPCServerError(e.message)

    def stop(self, process_name, wait=True):
        try:
            return self.__server.stopProcess(process_name, wait)
        except Exception, e:
            raise RPCServerError(e.message)

    def stopall(self, wait=True):
        try:
            for process in self.all_process():
                if process.statename == 'STOPPED':
                    continue
                else:
                    self.__server.stopProcess("%s:%s" % (process.group, process.name), wait)
        except Exception, e:
            raise RPCServerError(e.message)

    def startall(self, wait=True):
        try:
            for process in self.all_process():
                if process.statename == 'RUNNING':
                    continue
                else:
                    self.__server.startProcess("%s:%s" % (process.group, process.name), wait)
        except Exception, e:
            raise RPCServerError(e.message)

    def restartall(self, wait=True):
        try:
            self.stopall()
            self.startall()
        except Exception, e:
            raise RPCServerError(e.message)

