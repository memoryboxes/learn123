#encoding=utf-8
import os
import copy
from collections import OrderedDict
from .fields import BaseField, CommonFields, ItemField
from .exceptions import ValidationError, NON_FIELD_ERRORS
from .serializers import SerializerFactory
from .utils import ErrorDict, ErrorList, Dict, ReadOnlyDict, WriteableDict


def declared_field_value(value):
    if isinstance(value, (BaseField, CommonFields, ItemField)):
        return value
    elif isinstance(value, dict):
        return OrderedDict([(k, declared_field_value(v)) for k, v in value.iteritems()])
    elif isinstance(value, list):
        return [declared_field_value(v) for v in value]
    elif isinstance(value, tuple):
        return tuple([declared_field_value(v) for v in value])
    else:
        raise Exception("declared field value:%r is wrong type" % value)


class FieldsMetaclass(type):
    """
    Metaclass that collects Fields declared on the base classes.
    """
    def __new__(cls, name, bases, attrs):
        # Collect fields from current class.
        attrs['fields'] = declared_field_value(attrs.get("fields", {}))
        new_class = super(FieldsMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class


class BaseEntity(object):

    __metaclass__ = FieldsMetaclass

    fields = {}

    def __init__(self, data=None, **kwargs):
        self.initial(**kwargs)
        self._raw_data = data

    def initial(self, **kwargs):
        self.clear_errors()

    def _load(self, raw_data):
        """
        convert raw_data to data
        """
        data = self._clean_fields(raw_data)
        data = self._clean_config(data)
        self.raise_error()
        return data

    def _dump(self, data):
        """
        convert data to raw_data
        """
        data = self._validate(data)
        raw_data = self._dump_fields(data)
        self.raise_error()
        return raw_data

    def _validate(self, data):
        self._validate_fields(data)
        data = self._clean_config(data)
        self.raise_error()
        return data

    def _clean(self, data):
        """
        Hook for doing any extra config-wide cleaning after BaseField.clean() been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '__all__'.
        """
        return data

    def get_serializer(self):
        return SerializerFactory.create(None, self.fields, **self.get_serializer_context())

    def get_serializer_context(self):
        return {
            "error_strict": True,
            "dict_constructor": dict,
        }

    def _validate_fields(self, data):
        serializer = self.get_serializer()
        serializer.validate(data)
        for field_name, error in serializer.errors.iteritems():
            self.add_error(field_name, error)

    def _dump_fields(self, data):
        serializer = self.get_serializer()
        raw_data = serializer.dump(data)
        for field_name, error in serializer.errors.iteritems():
            self.add_error(field_name, error)
        return raw_data

    def _clean_fields(self, raw_data):
        serializer = self.get_serializer()
        cleaned_data = serializer.load(raw_data)
        for field_name, error in serializer.errors.iteritems():
            self.add_error(field_name, error)
        return cleaned_data

    def _clean_config(self, data):
        try:
            return self._clean(data)
        except ValidationError as e:
            self.add_error(NON_FIELD_ERRORS, e)

    def add_error(self, field, error):
        """
        Update the content of `self._errors`.

        The `field` argument is the name of the field to which the errors
        should be added. If its value is None the errors will be treated as
        NON_FIELD_ERRORS.

        The `error` argument can be a single error, a list of errors, or a
        dictionary that maps field names to lists of errors. What we define as
        an "error" can be either a simple string or an instance of
        ValidationError with its message attribute set and what we define as
        list or dictionary can be an actual `list` or `dict` or an instance
        of ValidationError with its `error_list` or `error_dict` attribute set.

        If `error` is a dictionary, the `field` argument *must* be None and
        errors will be added to the fields that correspond to the keys of the
        dictionary.
        """
        if not isinstance(error, ValidationError):
            # Normalize to ValidationError and let its constructor
            # do the hard work of making sense of the input.
            error = ValidationError(error)

        if hasattr(error, 'error_dict'):
            if field is not None:
                raise TypeError(
                    "The argument `field` must be `None` when the `error` "
                    "argument contains errors for multiple fields."
                )
            else:
                error = error.error_dict
        else:
            error = {field or NON_FIELD_ERRORS: error.error_list}

        for field, error_list in error.items():
            if field not in self._errors:
                self._errors[field] = ErrorList()
            self._errors[field].extend(error_list)

    def raise_error(self):
        if self._errors:
            raise ValidationError(self._errors.as_json())

    def clear_errors(self):
        self._errors = ErrorDict()


class BaseForm(BaseEntity):

    def initial(self):
        self.cleaned_data = None

    def raise_error(self, raise_exception=False):
        if raise_exception:
            super(BaseForm, self).raise_error()

    def validate(self, raise_exception=False):
        self.clear_errors()
        self.cleaned_data = None
        pipeline = [self._load, self._validate, self._clean]
        data = self._raw_data
        for pipe_func in pipeline:
            data = pipe_func(data)
            self.raise_error(raise_exception)
            if len(self._errors):
                return False
        self.cleaned_data = data
        return True

    def clean(self):
        return self.cleaned_data


class BaseConfig(BaseEntity):

    loader_class = None
    loader_context = {}

    def __init__(self, data=None, raw_data=None, init_load=True, **kwargs):
        self.initial(**kwargs)

        self._loader = self.get_loader()
        # need judge None because data/raw_data maybe empty-dict etc.
        if data is not None:
            _data = self.validate(data)
        elif raw_data is not None:
            _data = self.load(raw_data)
        elif init_load:
            _data = self.load(self._loader.load())
        else:
            # used for create a new file which not exist before.
            _data = {}
        self._origin_data = _data
        self._data = self.initial_data(_data)

    def readonly(self, data):
        if isinstance(data, dict):
            return ReadOnlyDict(data)
        elif isinstance(data, (list, tuple)):
            return tuple(self.readonly(_data) for _data in data)
        else:
            return copy.deepcopy(data)

    def writeable(self, data):
        if isinstance(data, dict):
            return WriteableDict(data)
        elif isinstance(data, (list, tuple)):
            return list(self.writeable(_data) for _data in data)
        else:
            return copy.deepcopy(data)

    def initial_data(self, data):
        return self.readonly(data)

    def get_loader_class(self):
        return self.loader_class

    def get_loader_context(self):
        return {}

    def get_loader(self):
        loader_class = self.get_loader_class()
        return loader_class(**dict(self.loader_context, **self.get_loader_context()))

    def validate(self, data):
        return super(BaseConfig, self)._validate(data)

    def _validate(self, data):
        return self.validate(data)

    def clean(self, data):
        return super(BaseConfig, self)._clean(data)

    def _clean(self, data):
        return self.clean(data)

    def load(self, data):
        return super(BaseConfig, self)._load(data)

    def _load(self, data):
        return self.load(data)

    def dump(self, data):
        return super(BaseConfig, self)._dump(data)

    def _dump(self, data):
        return self.dump(data)

    @classmethod
    def make(cls, data, raw=False, **kwargs):
        if raw:
            return cls(raw_data=data, **kwargs)
        else:
            return cls(data, **kwargs)


class FileConfig(BaseConfig):

    config_file = None

    @classmethod
    def get_file(cls, **kwargs):
        return cls.config_file

    def initial(self, **kwargs):
        super(FileConfig, self).initial(**kwargs)
        self._file = os.path.abspath(self.get_file(**kwargs))

    def get_loader_context(self):
        return {
            "file_path": self._file
        }

    @property
    def file(self):
        return self._file


class ReadMixin(object):

    def _get_data(self, data):
        if isinstance(data, dict):
            return Dict(data)
        elif isinstance(data, (list, tuple)):
            return type(data)(self._get_data(_data) for _data in data)
        else:
            return copy.deepcopy(data)

    @property
    def data(self):
        return self._get_data(self._origin_data)

    def get(self, key, default=None, writeable=False):
        data = self._data
        if not isinstance(data, dict):
            return default
        keys = key.split(".")
        for k in keys[:-1]:
            data = data.get(k, {})
        data = data.get(keys[-1], default)
        if writeable:
            data = self.writeable(data)
        return data


class WriteMixin(object):

    def _update(self, olddata, newdata):
        for key, value in newdata.iteritems():
            data = olddata
            keys = key.split(".")
            for k in keys[:-1]:
                if k not in data:
                    data[k] = {}
                data = data[k]
            data[keys[-1]] = value

    def update(self, value):
        if isinstance(self._origin_data, dict) and isinstance(value, dict):
            self._update(self._origin_data, value)
        else:
            self._origin_data = value
        self._data = self.initial_data(self._origin_data)

    def _deep_update(self, olddata, newdata):
        for key, value in newdata.iteritems():
            if isinstance(olddata.get(key), dict) and isinstance(value, dict):
                self._deep_update(olddata[key], value)
            else:
                olddata[key] = value

    def deep_update(self, value):
        if isinstance(self._origin_data, dict) and isinstance(value, dict):
            self._deep_update(self._origin_data, value)
        else:
            self._origin_data = value
        self._data = self.initial_data(self._origin_data)

    def save(self):
        self._loader.dump(self.dump(self._origin_data))


class ReadOnlyConfig(ReadMixin,
                     FileConfig):
    pass

class ReadWriteConfig(ReadMixin,
                      WriteMixin,
                      FileConfig):
    pass


class ConfigSet(object):

    def get_configs(self):
        raise NotImplemented()


class DirConfigSet(ConfigSet):

    config_dirs = ()
    config_class = None

    def __init__(self):
        self._files = tuple(self._get_files(self.get_dirs()))
        self._create()

    def _create(self):
        self._configs = []
        for file_path in self.get_files():
            self._configs.append(self.create_config(file_path))
        self._configs = tuple(self._configs)

    def create_config(self, file_path):
        return self.config_class(file_path=file_path)

    @classmethod
    def get_dirs(self):
        return self.config_dirs

    def _ignore_file_name(self, file_name):
        if file_name.endswith(".xml"):
            return False
        return True

    def _get_files(self, config_dirs, deep=False):
        if config_dirs:
            if isinstance(config_dirs, basestring):
                config_dirs = [config_dirs, ]
            config_files = set()
            for config_dir in config_dirs:
                if not config_dir:
                    continue
                if deep:
                    for root, dirs, files in os.walk(config_dir):
                        for file_name in files:
                            if self._ignore_file_name(file_name):
                                continue
                            file_path = os.path.abspath(os.path.join(root, file_name))
                            if file_path not in config_files:
                                config_files.add(file_path)
                                yield file_path
                else:
                    for dir_name in os.listdir(config_dir):
                        root = os.path.join(config_dir, dir_name)
                        if os.path.isdir(root):
                            for file_name in os.listdir(root):
                                if self._ignore_file_name(file_name):
                                    continue
                                file_path = os.path.abspath(os.path.join(root, file_name))
                                if os.path.isfile(file_path) and file_path not in config_files:
                                    config_files.add(file_path)
                                    yield file_path

    def get_files(self):
        return self._files

    def get_configs(self):
        return self._configs
