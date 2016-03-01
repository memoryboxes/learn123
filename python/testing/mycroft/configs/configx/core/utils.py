#encoding=utf-8
import json
import copy
from inspect import isgenerator
from UserList import UserList
from .exceptions import ValidationError


def humanize_bytes(n, precision=2):
    # Author: Doug Latornell
    # Licence: MIT
    # URL: http://code.activestate.com/recipes/577081/
    """Return a humanized string representation of a number of bytes.

    Assumes `from __future__ import division`.

    >>> humanize_bytes(1)
    '1 B'
    >>> humanize_bytes(1024, 1)
    '1.0 kB'
    >>> humanize_bytes(1024 * 123, 1)
    '123.0 kB'
    >>> humanize_bytes(1024 * 12342, 1)
    '12.1 MB'
    >>> humanize_bytes(1024 * 12342, 2)
    '12.05 MB'
    >>> humanize_bytes(1024 * 1234, 2)
    '1.21 MB'
    >>> humanize_bytes(1024 * 1234 * 1111, 2)
    '1.31 GB'
    >>> humanize_bytes(1024 * 1234 * 1111, 1)
    '1.3 GB'

    """
    abbrevs = [
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'B')
    ]

    if n == 1:
        return '1 B'

    for factor, suffix in abbrevs:
        if n >= factor:
            break

    return '%.*f %s' % (precision, float(n) / factor, suffix)


undefined = object()

class ErrorDict(dict):
    """
    A collection of errors that knows how to display itself in json formats.

    The dictionary keys are the field names, and the values are the errors.
    """
    def as_data(self):
        x = {}
        for f, e in self.items():
            parts = f.split(".")
            v = x
            for part in parts[:-1]:
                if part not in x:
                    v[part] = {}
                v = v[part]
            v[parts[-1]] = e.as_data()
        return x

    def as_json(self, **kwargs):
        x = {}
        for f, e in self.items():
            parts = f.split(".")
            v = x
            for part in parts[:-1]:
                if part not in x:
                    v[part] = {}
                v = v[part]
            v[parts[-1]] = e.get_json_data()
        return json.dumps(x, **kwargs)

    def __str__(self):
        return self.as_json()


class ErrorList(UserList, list):
    """
    A collection of errors that knows how to display itself in json formats.
    """
    def as_data(self):
        return ValidationError(self.data).error_list

    def get_json_data(self):
        errors = []
        for error in self.as_data():
            message = list(error)[0]
            errors.append(message)
        return errors

    def as_json(self, **kwargs):
        return json.dumps(self.get_json_data(), **kwargs)

    def __str__(self):
        return self.as_json()

    def __repr__(self):
        return repr(list(self))

    def __contains__(self, item):
        return item in list(self)

    def __eq__(self, other):
        return list(self) == other

    def __ne__(self, other):
        return list(self) != other

    def __getitem__(self, i):
        error = self.data[i]
        if isinstance(error, ValidationError):
            return list(error)[0]
        return error.message

    def __reduce_ex__(self, *args, **kwargs):
        # The `list` reduce function returns an iterator as the fourth element
        # that is normally used for repopulating. Since we only inherit from
        # `list` for `isinstance` backward compatibility (Refs #17413) we
        # nullify this iterator as it would otherwise result in duplicate
        # entries. (Refs #23594)
        info = super(UserList, self).__reduce_ex__(*args, **kwargs)
        return info[:3] + (None, None)

class Dict(dict):

    def __init__(self, *args, **kwargs):
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    self[key] = val
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                self[arg[0]] = arg[1]
            elif isinstance(arg, (list, tuple)) or isgenerator(arg):
                for key, val in arg:
                    self[key] = val
            else:
                raise TypeError("Dict does not understand "
                                    "{0} types".format(type(arg)))

        for key, val in kwargs.items():
            self[key] = val

    def __setattr__(self, name, value):
        """
        setattr is called when the syntax a.b = 2 is used to set a value.
        """
        if hasattr(Dict, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        """
        This is called when trying to set a value of the Dict using [].
        E.g. some_instance_of_Dict['b'] = val. If 'val
        """
        value = self._hook(value)
        super(Dict, self).__setitem__(name, value)

    @classmethod
    def _hook(cls, item):
        """
        Called to ensure that each dict-instance that are being set
        is a addict Dict. Recurses.
        """
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, name):
        """
        This is called when the Dict is accessed by []. E.g.
        some_instance_of_Dict['a'];
        If the name is in the dict, we return it. Otherwise we set both
        the attr and item to a new instance of Dict.
        """
        if name not in self:
            self[name] = {}
        return super(Dict, self).__getitem__(name)

    def __delattr__(self, name):
        """
        Is invoked when del some_instance_of_Dict.b is called.
        """
        del self[name]

    def __dir__(self):
        """
        Is invoked on a Dict instance causes __getitem__() to get invoked
        which in this module will trigger the creation of the following
        properties: `__members__` and `__methods__`
        To avoid these keys from being added, we simply return an explicit
        call to dir for the Dict object
        """
        return dir(Dict)

    def __deepcopy__(self, memo):
        y = {}
        memo[id(self)] = y
        for key, value in self.iteritems():
            y[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return y

    def _ipython_display_(self):
        print(str(self))    # pragma: no cover

    def _repr_html_(self):
        return str(self)

    def prune(self, prune_zero=False, prune_empty_list=True):
        """
        Removes all empty Dicts and falsy stuff inside the Dict.
        E.g
        >>> a = Dict()
        >>> a.b.c.d
        {}
        >>> a.a = 2
        >>> a
        {'a': 2, 'b': {'c': {'d': {}}}}
        >>> a.prune()
        >>> a
        {'a': 2}
        Set prune_zero=True to remove 0 values
        E.g
        >>> a = Dict()
        >>> a.b.c.d = 0
        >>> a.prune(prune_zero=True)
        >>> a
        {}
        Set prune_empty_list=False to have them persist
        E.g
        >>> a = Dict({'a': []})
        >>> a.prune()
        >>> a
        {}
        >>> a = Dict({'a': []})
        >>> a.prune(prune_empty_list=False)
        >>> a
        {'a': []}
        """
        for key, val in list(self.items()):
            if ((not val) and ((val != 0) or prune_zero) and
                not isinstance(val, list)):
                del self[key]
            elif isinstance(val, Dict):
                val.prune(prune_zero, prune_empty_list)
                if not val:
                    del self[key]
            elif isinstance(val, (list, tuple)):
                new_iter = self._prune_iter(val, prune_zero, prune_empty_list)
                if (not new_iter) and prune_empty_list:
                    del self[key]
                else:
                    if isinstance(val, tuple):
                        new_iter = tuple(new_iter)
                    self[key] = new_iter

    @classmethod
    def _prune_iter(cls, some_iter, prune_zero=False, prune_empty_list=True):
        new_iter = []
        for item in some_iter:
            if item == 0 and prune_zero:
                continue
            elif isinstance(item, Dict):
                item.prune(prune_zero, prune_empty_list)
                if item:
                    new_iter.append(item)
            elif isinstance(item, (list, tuple)):
                new_item = type(item)(
                    cls._prune_iter(item, prune_zero, prune_empty_list))
                if new_item or not prune_empty_list:
                    new_iter.append(new_item)
            else:
                new_iter.append(item)
        return new_iter

    def to_dict(self):
        """
        Recursively turn your addict Dicts into dicts.
        """
        base = dict()
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base


class WriteableDict(Dict):

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return list(cls._hook(elem) for elem in item)
        return item

class ReadOnlyDict(Dict):

    _readonly = False

    def __init__(self, data):
        super(ReadOnlyDict, self).__init__(data)
        self._readonly = True

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return tuple(cls._hook(elem) for elem in item)
        return item

    def __setitem__(self, *args, **kwargs):
        if self._readonly:
            raise TypeError
        return super(ReadOnlyDict, self).__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        if self._readonly:
            raise TypeError
        return super(ReadOnlyDict, self).__delitem__(*args, **kwargs)

    def __getitem__(self, name):
        if name not in self:
            return ReadOnlyDict({})
        return super(Dict, self).__getitem__(name)

    def clear(self):
        if self._readonly:
            raise TypeError
        return super(ReadOnlyDict, self).clear()

    def pop(self, *args, **kwargs):
        if self._readonly:
            raise TypeError
        return super(ReadOnlyDict, self).pop(*args, **kwargs)

    def popitem(self):
        if self._readonly:
            raise TypeError
        return super(ReadOnlyDict, self).popitem()

    def __setattr__(self, name, value):
        if self._readonly:
            raise TypeError
        if name in ['_data', '_readonly']:
            return object.__setattr__(self, name, value)
        return super(ReadOnlyDict, self).__setattr__(name, value)

    def prune(self, *args, **kwargs):
        if self._readonly:
            raise TypeError
        return super(ReadOnlyDict, self).prune(*args, **kwargs)
