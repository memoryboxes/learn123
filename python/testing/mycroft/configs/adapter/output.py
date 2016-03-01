#encoding=utf-8
import io
import os
import time
import socket
import logging
from .utils import new_thread

logger = logging.getLogger("default")

class Output(object):

    def __init__(self):
        self._count = 0

    def output(self, record):
        self._output(record)
        self._count += 1

    def _output(self):
        raise NotImplementedError()

    def close(self):
        return

    def get_value(self):
        return None

    def empty(self):
        return bool(self.count)

    @property
    def count(self):
        return self._count

class StreamOutput(Output):

    def __init__(self, stream):
        self.stream = stream
        super(StreamOutput, self).__init__()

    def _output(self, record):
        self.stream.write(record)


class StringOutput(Output):

    def __init__(self):
        self.data = []
        super(StringOutput, self).__init__()

    def _output(self, record):
        self.data.append(record)

    def get_value(self):
        return "\n".join(self.data)


class ListOutput(Output):

    def __init__(self, store=None):
        if store is None:
            self.store = []
        else:
            self.store = store
        super(ListOutput, self).__init__()

    def _output(self, record):
        self.store.append(record)

    def get_value(self):
        return self.store


class FuncOutput(Output):

    def __init__(self, func):
        self.func = func
        super(FuncOutput, self).__init__()

    def _output(self, record):
        self.func(record)


class FileOutput(Output):

    def __init__(self, file_path,
                 mode="wb",
                 tmp_suffix=None,
                 exists='warning',
                 create=True,
                 line_break='\n',
                 encoding="utf-8",
                 fopen="open",
                 mkdir=2):
        self._file_path = os.path.abspath(file_path)
        self._mode = mode
        self._tmp_suffix = tmp_suffix
        self._exists = exists
        self._create = create
        self._stream = None
        self._line_break = line_break
        self._encoding = encoding
        self._fopen = fopen
        self._mkdir = mkdir
        super(FileOutput, self).__init__()
        if os.path.exists(self._file_path):
            if self._exists == 'warning':
                logger.warning("File %s already exists." %self._file_path)
            elif self._exists == 'error':
                raise Exception("File %s already exists." %self._file_path)

    @property
    def write_file_path(self):
        if self._tmp_suffix:
            return '%s.%s' %(self._file_path, self._tmp_suffix)
        else:
            return self._file_path

    @property
    def stream(self):
        if not self._stream:
            if os.path.exists(self._file_path):
                if self._exists == 'warning':
                    logger.warning("File %s already exists." %self._file_path)
                elif self._exists == 'error':
                    raise Exception("File %s already exists." %self._file_path)
            if self._mkdir:
                base_path = os.path.dirname(self._file_path)
                if not os.path.exists(base_path):
                    if self._mkdir > 1:
                        os.makedirs(base_path)
                    else:
                        os.mkdir(base_path)
            self._stream = self._open(self.write_file_path, self._mode)
        return self._stream

    def _open(self, file_path, mode):
        if self._fopen == "io.open":
            if "b" not in mode:
                return io.open(file_path, mode, encoding=self._encoding)
            else:
                return io.open(file_path, mode)
        else:
            return open(file_path, mode)

    def _output(self, record):
        self.stream.write(record)
        if self._line_break:
            self.stream.write(self._line_break)
        self.stream.flush()

    @new_thread()
    def _async_rename(self, retry=0):
        self._rename(retry)

    def _rename(self, retry=0):
        if self._tmp_suffix:
            try:
                os.rename(self.write_file_path, self._file_path)
            except OSError:
                if retry > 0:
                    time.sleep(1)
                    self._rename(retry - 1)
                else:
                    logger.exception("Rename file error from %s to %s.",
                                     self.write_file_path, self._file_path)

    def close(self):
        if self._stream:
            self._stream.close()
            self._async_rename(3)
            self._stream = None

    def empty(self):
        if os.path.isfile(self.write_file_path):
            if os.stat(self.write_file_path).st_size > 0:
                return False
        return True


class UDPOutput(Output):


    def __init__(self, endpoint):
        self.host, self.port = self.get_endpoint(endpoint)
        super(UDPOutput, self).__init__()

    def get_endpoint(self, endpoint):
        '''
        endpoint:
              <host>: <port>
              {'host': <host>, 'port': <port>}
              (<host>, <port>)
              object<host, port>
        '''
        host = None
        port = None
        try:
            if isinstance(endpoint, dict):
                host = endpoint.get('host')
                port = endpoint.get('port')
            elif isinstance(endpoint, (list, tuple)):
                host = endpoint[0]
                port = endpoint[1]
            elif isinstance(endpoint, basestring):
                host_port = endpoint.split(':')
                host = host_port[0].strip()
                port = host_port[1].strip()
            else:
                host = endpoint.host
                port = endpoint.port
        except:
            pass
        return host, int(port)

    def _output(self, record):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(record, (self.host, self.port))
        sock.close()
