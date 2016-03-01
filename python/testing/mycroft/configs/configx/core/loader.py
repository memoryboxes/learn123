#encoding=utf-8
import copy
import xmltodict
from collections import OrderedDict
from mycroft.configs.adapter import XMLAdapter
from mycroft.configs.adapter.utils import encode, decode
from ConfigParser import RawConfigParser as ConfigParser


class FileLoader(object):

    suffix = ""

    def __init__(self, file_path):
        self._file = file_path

    def load(self):
        raise NotImplementedError()

    def dump(self):
        raise NotImplementedError()

    @classmethod
    def build(cls, **kwargs):
        _kwargs = kwargs
        def construct(*args, **kwargs):
            return cls(**dict(_kwargs, **kwargs))
        construct.suffix = cls.suffix
        return construct


class MemFileLoader(FileLoader):

    suffix = "mem"
    mem = {}

    def __init__(self, file_path, mem=None):
        super(MemFileLoader, self).__init__(file_path)
        if mem is not None:
            self.mem = mem

    def load(self):
        return copy.deepcopy(self.mem.get(self._file))

    def dump(self, doc):
        self.mem[self._file] = doc


class XMLLoader(FileLoader):

    suffix = "xml"

    def __init__(self, file_path, root=None):
        super(XMLLoader, self).__init__(file_path)
        self._root = root

    def load(self):
        with open(self._file, "rb") as fp:
            doc = xmltodict.parse(fp, dict_constructor=OrderedDict)
        if self._root:
            doc = doc[self._root]
        return doc

    def dump(self, doc):
        if self._root:
            doc = {
                self._root: doc
            }
        adapter = XMLAdapter(self._file)
        adapter.write(doc)


class PartXMLLoader(XMLLoader):

    def __init__(self, file_path, root):
        super(XMLLoader, self).__init__(file_path)
        self._root = root

    def load(self):
        with open(self._file, "rb") as fp:
            data = "<{root}>{data}</{root}>".format(root=self._root, data=fp.read())
            doc = xmltodict.parse(data, dict_constructor=OrderedDict)
        return doc[self._root]

    def dump(self, doc):
        # below way to unparse, the output text is not enough pretty
        #doc = xmltodict.unparse({"root": doc}, full_document=False, pretty=True)

        doc = xmltodict.unparse({"root": doc}, pretty=True, indent="    ")
        doc = doc.split("\n")[2:-1]
        doc = [line[4:] for line in doc]
        doc = "\n".join(doc)
        with open(self._file, 'wb') as fp:
            fp.write(doc)


class INILoader(FileLoader):

    suffix = "ini"

    def load(self):
        doc = OrderedDict()
        with open(self._file, "rb") as fp:
            config = ConfigParser()
            config.readfp(fp)
            for section in config.sections():
                doc[section] = OrderedDict(config.items(section))
        return doc

    def dump(self, doc):
        doc = doc or {}
        config = ConfigParser()
        for section, item in doc.iteritems():
            config.add_section(section)
            for key, value in item.iteritems():
                config.set(section, key, value)
        with open(self._file, "wb") as fp:
            config.write(fp)


class CfgLoader(INILoader):

    suffix = "cfg"


class ConfLoader(FileLoader):

    suffix = "conf"

    def __init__(self, file_path, separator=":", sub_section="#name", charset="utf-8"):
        super(ConfLoader, self).__init__(file_path)
        self._sep = separator or ""
        self._sub = sub_section
        self._charset = charset

    def _split(self, section):
        if self._sep:
            return section.split(self._sep, 1)
        else:
            return [section]

    def _join(self, sections):
        if self._sep:
            return self._sep.join(sections)
        else:
            return sections[0]

    def load(self):
        doc = OrderedDict()
        with open(self._file, "rb") as fp:
            config = ConfigParser()
            config.optionxform = str
            config.readfp(fp)
            for section in config.sections():
                sections = self._split(section)
                top_section = sections[0]
                sub_doc = None
                if top_section in doc:
                    sub_doc = OrderedDict()
                    if not isinstance(doc[top_section], list):
                        doc[top_section] = [doc[top_section]]
                    doc[top_section].append(sub_doc)
                else:
                    sub_doc = doc[top_section] = OrderedDict()
                if len(sections) > 1:
                    sub_doc[self._sub] = sections[1]
                for key, value in config.items(section):
                    sub_doc[key] = value
        return decode(doc, self._charset)

    def dump(self, doc):
        doc = encode(doc or {}, self._charset)
        config = ConfigParser()
        config.optionxform = str

        def set_sub_section(top_section, item):
            sections = [top_section]
            if self._sub in item:
                sections.append(item[self._sub])
            section = self._join(sections)
            config.add_section(section)
            for key, value in item.iteritems():
                if key == self._sub:
                    continue
                config.set(section, key, value)

        for section, item in doc.iteritems():
            if not isinstance(item, (list, tuple)):
                item = [item]
            for _item in item:
                set_sub_section(section, _item)

        with open(self._file, "wb") as fp:
            config.write(fp)
