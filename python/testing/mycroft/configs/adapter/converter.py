#encoding=utf-8
import logging
from inspect import isgenerator

logger = logging.getLogger("default")

def listable(value):
    return isinstance(value, (list, tuple)) or isgenerator(value)


class BaseConverter(object):


    def convert(self, data):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.convert(*args, **kwargs)


class TypeConverter(BaseConverter):

    #list, tuple, iter, none
    special_types = (
        'none',
    )
    def type_list(self, data):
        return isinstance(data, list)

    def type_tuple(self, data):
        return isinstance(data, tuple)

    def type_iter(self, data):
        return isgenerator(data)

    def type_none(self, data):
        return data is None

    def convert(self, data):
        convert_func = self.convert_value
        for type_name in self.special_types:
            check_func = getattr(self, "type_%s" %type_name)
            if check_func(data):
                convert_func = getattr(self, "convert_%s" %type_name, convert_func)
        return convert_func(data)

    def convert_value(self):
        raise NotImplementedError()

    def convert_none(self):
        return None

class ListConverter(TypeConverter):

    special_types = (
        "list", "tuple", "iter", "none"
    )

    def convert_value(self, data):
        return [data]

    def convert_none(self, data):
        return []

    def convert_list(self, data):
        return data

    def convert_tuple(self, data):
        return list(data)

    def convert_iter(self, data):
        return [d for d in data]

class FuncConverter(TypeConverter):

    def __init__(self, funcs, extra_types=None):
        self.special_types = set(FuncConverter.special_types)
        if isinstance(funcs, dict):
            for key, func in funcs.iteritems():
                self.special_types.add(key)
                setattr(self, "convert_%s" %key, func)
        else:
            self.convert_value = funcs
        if extra_types:
            for key, func in extra_types:
                setattr(self, "type_%s" %key, func)
