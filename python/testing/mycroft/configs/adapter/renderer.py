#encoding=utf-8
import csv
import json
import xmltodict
import msgpack
from inspect import isgenerator
from jinja2 import Template
from .utils import encode, decode
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO


class BaseRenderer(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.initial()

    def initial(self):
        return

    def encode(self, data, charset):
        return encode(data, charset)

    def decode(self, data, charset):
        return decode(data, charset)

    def _render(self, data, **kwargs):
        raise NotImplementedError()

    def render(self, data, **kwargs):
        return self._render(data, **dict(self.kwargs, **kwargs))


class DataJSONRenderer(BaseRenderer):

    def _render(self, data, *args, **kwargs):
        return json.dumps(self.decode(data, 'utf-8'), *args, **kwargs)


class DataMsgPackRenderer(BaseRenderer):

    def _render(self, data, *args, **kwargs):
        return msgpack.packb(data, *args, **kwargs)


class DataJoinRenderer(BaseRenderer):

    def decode(self, data, charset):
        if not isinstance(data, basestring):
            data = str(data)
        return super(DataJoinRenderer, self).decode(data, charset)

    def _render(self, data, fields=None, delimiter='|', *args, **kwargs):
        if not isinstance(delimiter, unicode):
            delimiter = self.decode(delimiter, 'utf-8')
        data = data or {}
        if isinstance(data, (list, tuple)):
            return delimiter.join(self.decode(data, 'utf-8'))
        else:
            fields = fields or sorted(data.keys())
            return delimiter.join([self.decode(data.get(k, ""), 'utf-8') for k in fields])


class RowCSVRenderer(BaseRenderer):

    def _render_row(self, writer, data):
        writer.writerow(data)

    def _render(self, data, fields=None, header=True, **kwargs):
        stream = StringIO()
        if isinstance(data, dict):
            fields = fields or sorted(data.keys())
            writer = csv.DictWriter(stream, fields, **kwargs)
            if header:
                self._render_row(writer, {
                    field: self.encode(field, 'utf-8') for field in fields
                })
            row = {}
            for k in fields:
                if k in data:
                    row[k] = self.encode(data[k], 'utf-8')
                else:
                    row[k] = ""
            self._render_row(writer, row)
        else:
            writer = csv.writer(stream, **kwargs)
            if header:
                self._render_row(writer, [
                    self.encode(field, 'utf-8') for field in fields
                ])
            self._render_row(writer, [self.encode(d, 'utf-8') for d in data])

        result = stream.getvalue()
        stream.close()
        return result.decode("utf-8")


class DataCSVRenderer(RowCSVRenderer):

    def _render(self, data, fields=None, header=True, **kwargs):
        stream = StringIO()
        writer = None
        if data:
            if not isinstance(data, (list, tuple)) and not isgenerator(data):
                data = [data]
        for d in data:
            if isinstance(d, dict):
                if writer is None:
                    fields = fields or sorted(d.keys())
                    writer = csv.DictWriter(stream, fields, **kwargs)
                    if header:
                        self._render_row(writer, {
                            field: self.encode(field, 'utf-8') for field in fields
                        })
                row = {}
                for k in fields:
                    if k in d:
                        row[k] = self.encode(d[k], 'utf-8')
                    else:
                        row[k] = ""
                self._render_row(writer, row)
            else:
                if writer is None:
                    writer = csv.writer(stream, **kwargs)
                    if header:
                        self._render_row(writer, [
                            self.encode(field, 'utf-8') for field in fields
                        ])
                self._render_row(writer, [self.encode(_d, 'utf-8') for _d in d])

        result = stream.getvalue()
        stream.close()
        return result.decode("utf-8")


class DataXMLRenderer(BaseRenderer):

    def _render(self, data, indent=4, root="result", **kwargs):
        indent = indent * " "
        if isinstance(data, dict):
            if len(data) > 1:
                data = {
                    root: data
                }
        elif isinstance(data, (list, tuple)) or isgenerator(data):
            data = {
                root: {
                    "record": list(data)
                }
            }
        else:
            data = {
                root: data
            }
        data = self.decode(data, "utf-8")
        return xmltodict.unparse(data, pretty=True, indent=indent, **kwargs)


class DataTemplateRenderer(BaseRenderer):

    def _render(self, data, template, encoding="utf-8", **kwargs):
        if not isinstance(data, dict):
            data = {
                "result": data
            }
        with open(template, "rb") as fp:
            template = Template(fp.read().decode(encoding))
            data = self.decode(data, "utf-8")
            return template.render(data, charset="utf-8")
