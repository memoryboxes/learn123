#encoding=utf-8
import os
import msgpack
from .renderer import (
    RowCSVRenderer,
    DataXMLRenderer,
    DataJSONRenderer,
    DataMsgPackRenderer,
    DataTemplateRenderer,
    DataJoinRenderer,
)
from .output import (
    UDPOutput,
    FileOutput,
)

class Adapter(object):

    def __init__(self):
        self.converters = []
        self._writed = False

    @property
    def writed(self):
        return self._writed

    def add_converter(self, converter):
        self.converters.append(converter)

    def set_converters(self, converters):
        self.converters = converters

    def _write(self, data, **kwargs):
        raise NotImplementedError()

    def write(self, data, **kwargs):
        for converter in self.converters:
            data = converter(data)
        self._write(data, **kwargs)
        self._writed = True

class StreamAdapter(Adapter):

    def close(self):
        raise NotImplementedError()


class CSVAdapter(StreamAdapter):

    def __init__(self, file_path,
                 header=False,
                 fields=None,
                 delimiter=',',
                 quotechar='"',
                 tmp_suffix=None,
                 charset='utf-8',
                 exists='warning',
                 write_mode='a',
                 mkdir=2):
        self.renderer = RowCSVRenderer(fields=fields, delimiter=delimiter, quotechar=quotechar)
        self.output = FileOutput(file_path,
                                 mode=write_mode,
                                 tmp_suffix=tmp_suffix,
                                 exists=exists,
                                 line_break="",
                                 mkdir=mkdir)
        self.header = header
        self.charset = charset
        super(CSVAdapter, self).__init__()

    def _write(self, data, **kwargs):
        header = False
        if not self.writed:
            if self.output.empty():
                header = self.header
        charset = kwargs.pop('charset', self.charset)
        header = kwargs.pop('header', header)
        self.output.output(self.renderer.render(data, header=header, **kwargs).encode(charset))

    def close(self):
        self.output.close()

class JSONAdapter(StreamAdapter):

    def __init__(self, file_path,
                 tmp_suffix=None,
                 charset='utf-8',
                 exists='warning',
                 write_mode="a",
                 mkdir=2):
        self.renderer = DataJSONRenderer()
        self.output = FileOutput(file_path,
                                 mode=write_mode,
                                 tmp_suffix=tmp_suffix,
                                 exists=exists,
                                 line_break=unicode("\n"),
                                 fopen="io.open",
                                 encoding=charset,
                                 mkdir=mkdir)
        self.charset = charset
        super(JSONAdapter, self).__init__()

    def _write(self, data, **kwargs):
        kwargs = dict(kwargs, ensure_ascii=False)
        kwargs.pop('charset', self.charset)
        record = self.renderer.render(data, **kwargs)
        self.output.output(unicode(record))

    def close(self):
        self.output.close()


class MsgPackAdapter(StreamAdapter):

    def __init__(self, file_path,
                 tmp_suffix=None,
                 charset='utf-8',
                 exists='warning',
                 write_mode='ab',
                 mkdir=2):
        self.renderer = DataMsgPackRenderer()
        self.output = FileOutput(file_path,
                                 mode=write_mode,
                                 tmp_suffix=tmp_suffix,
                                 exists=exists,
                                 encoding=charset,
                                 mkdir=mkdir)
        self.charset = charset
        super(MsgPackAdapter, self).__init__()

    def _write(self, data, **kwargs):
        kwargs.pop('charset', self.charset)
        record = self.renderer.render(data, **kwargs)
        self.output.output(record)

    def close(self):
        self.output.close()

class StreamWriteCache(object):

    def __init__(self, file_path, charset='utf-8', suffix="cache"):
        self.file_path = "%s.%s" % (file_path, suffix)
        self.charset = charset
        self._adapter = MsgPackAdapter(self.file_path, tmp_suffix=None, charset=self.charset)
        self._mem_cache = []
        self._mem_max_count = 1000
        self._total_count = 0

    def add(self, data):
        if len(self._mem_cache) < self._mem_max_count:
            self._mem_cache.append(data)
        else:
            for mdata in self._mem_cache:
                self._adapter.write(mdata)
            self._adapter.write(data)
            self._mem_cache = []
        self._total_count += 1

    def items(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as fp:
                for data in msgpack.Unpacker(fp, encoding=self.charset):
                    yield data

        for mdata in self._mem_cache:
            yield mdata

    @property
    def count(self):
        return self._total_count

    def clear(self):
        self._mem_cache = []
        self._total_count = 0
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
            except:
                pass

    def close(self):
        self._adapter.close()


class XMLAdapter(StreamAdapter):

    def __init__(self, file_path, indent=4, charset='utf-8', tmp_suffix='tmp', root='result', flush_count=1000):
        self.file_path = file_path
        self.charset = charset
        self.tmp_suffix = tmp_suffix
        self.flush_count = flush_count
        self.renderer = DataXMLRenderer(indent=indent, root=root)
        self.cache = StreamWriteCache(file_path, charset=charset)
        self.write_kwargs = None
        self.last_flush_count = 0
        super(XMLAdapter, self).__init__()

    def _write(self, data, **kwargs):
        self.cache.add(data)
        self.write_kwargs = kwargs

        if self.cache.count - self.last_flush_count >= self.flush_count:
            self._flush_write(self.cache.items())
            self.last_flush_count = self.cache.count

    def _flush_write(self, data, closed=False):
        if data:
            charset = self.write_kwargs.pop('charset', self.charset)
            data = self.renderer.render(data, **self.write_kwargs).encode(charset)
            output = FileOutput(self.file_path, mode="wb", tmp_suffix=self.tmp_suffix)
            output.output(data)
            if closed:
                output.close()

    def close(self):
        self._flush_write(self.cache.items(), closed=True)
        self.cache.clear()
        self.cache.close()


class TemplateAdapter(StreamAdapter):

    def __init__(self, file_path, template, charset='utf-8', tmp_suffix='tmp', flush_count=1000):
        self.file_path = file_path
        self.charset = charset
        self.tmp_suffix = tmp_suffix
        self.flush_count = flush_count
        self.renderer = DataTemplateRenderer(template=template)
        self.cache = StreamWriteCache(file_path, charset=charset)
        self.write_kwargs = None
        self.last_flush_count = 0
        super(TemplateAdapter, self).__init__()

    def _write(self, data, **kwargs):
        self.cache.add(data)
        self.write_kwargs = kwargs

        if self.cache.count - self.last_flush_count >= self.flush_count:
            self._flush_write(self.cache.items())
            self.last_flush_count = self.cache.count

    def _flush_write(self, data, closed=False):
        if data:
            charset = self.write_kwargs.pop('charset', self.charset)
            data = self.renderer.render(data, **self.write_kwargs).encode(charset)
            output = FileOutput(self.file_path, mode="wb", tmp_suffix=self.tmp_suffix)
            if closed:
                output.output(data)

    def close(self):
        self._flush_write(self.cache.items(), closed=True)
        self.cache.clear()
        self.cache.close()

class SyslogAdapter(StreamAdapter):

    FACILITY = {
        'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
        'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
        'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
        'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
        'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
    }

    LEVEL = {
        'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
        'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
    }

    def __init__(self, endpoint,
                 facility='daemon',
                 level='notice',
                 seperator='|',
                 fields=None,
                 charset='utf-8'):
        self.renderer = DataJoinRenderer(fields=fields, delimiter=seperator)
        self.output = UDPOutput(endpoint)
        self.level = self.LEVEL[level]
        self.facility = self.FACILITY[facility]
        self.charset = charset
        super(SyslogAdapter, self).__init__()

    def _write(self, data, **kwargs):
        level = kwargs.pop('level', self.level)
        facility = kwargs.pop('facility', self.facility)
        charset = kwargs.pop('charset', self.charset)
        record = self.renderer.render(data, **kwargs).encode(charset)
        record = '<%d>%s' % (level + facility*8, record)
        self.output.output(record)

    def close(self):
        return


from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import
class SOAPAdapter(StreamAdapter):

    def __init__(self, endpoint, function=None, params=None, get_params=None, callback=None):
        self.endpoint = endpoint
        self.function = function
        self.params = params
        self.get_params = get_params
        self.callback = callback
        super(SOAPAdapter, self).__init__()

    @property
    def client(self):
        if not hasattr(self, '_client'):
            imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
            self._client = Client(self.endpoint, doctor=ImportDoctor(imp))
        return self._client

    def _write(self, data=None, **kwargs):
        function = kwargs.pop('function', self.function)
        params = kwargs.pop('params', self.params)
        if params is None:
            get_params = kwargs.pop('get_params', self.get_params)
            if get_params:
                params = get_params(data)
            else:
                params = {}
        callback = kwargs.pop("callback", self.callback)
        result = getattr(self.client.service, function)(**params)
        if callback:
            callback(result)
        return result


    def close(self):
        self._client = None
