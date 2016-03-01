# -*- coding: utf-8 -*-
import os
import re
import copy
import json
import functools
from collections import OrderedDict
from os.path import isdir
from os.path import isfile
from os.path import exists as path_exists
from .exceptions import (
    ValidationError,
    FieldError,
)
from .utils import undefined, humanize_bytes

class FieldName(object):

    def __init__(self, name, optional=False, alias=None, **kwargs):
        self.name = name
        self.optional = optional
        self.alias = alias
        if optional:
            self.default = kwargs.get('default', undefined)
        else:
            self.default = undefined

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, FieldName):
            return other.name == self.name
        return self.name == other


class FieldMeta(type):

    def __new__(metaclass, name, bases, attrs):
        validators = OrderedDict()
        error_messages = {}
        converter = None

        for base in reversed(bases):
            if hasattr(base, '_validators'):
                validators.update(OrderedDict([(v.__name__, v) for v in base._validators]))
            if hasattr(base, '_error_messages'):
                error_messages.update(base._error_messages)

        for attr_name, value in attrs.iteritems():
            if attr_name.startswith('validate_') and callable(value):
                validators.update({attr_name: value})
            if attr_name == 'error_messages':
                error_messages.update(value)
            if attr_name.startswith('convert_') and callable(value):
                converter = value

        attrs['_validators'] = validators.values()
        attrs['_error_messages'] = error_messages
        if converter:
            attrs['_field_type'] = converter.__name__.split('_')[1]
            attrs['_converter'] = converter

        return type.__new__(metaclass, name, bases, attrs)


class BaseField(object):

    __metaclass__ = FieldMeta

    error_messages = {
        'convert_error': 'The value {_value} can not be converted to type {_type}',
    }

    def __init__(self, validators=None, error_messages=None):
        self.validators = [functools.partial(v, self) for v in self._validators] + (validators or [])
        self.error_messages = self._error_messages
        if hasattr(self, '_converter'):
            self.converter = self._converter
        if error_messages:
            self.error_messages.update(error_messages)

    def validate(self, value):
        value = self.try_convert(value)
        for validator in self.validators:
            validator(value)

    def try_convert(self, value):
        if hasattr(self, 'converter') and callable(self.converter):
            try:
                return self.converter(value)
            except (ValueError, TypeError):
                raise ValidationError(self.error_messages['convert_error'].format(_value=value, _type=self._field_type))
            except ValidationError, e:
                raise e
        return value

    def load(self, value):
        self.validate(value)
        if hasattr(self, 'converter') and callable(self.converter):
            return self.converter(value)
        return value

    def dump(self, value):
        self.validate(value)
        return value


class DictField(BaseField):

    error_messages = {
        'empty': 'The value {value} is empty',
        'type': 'The value type {vtype} should be a dictionary',
    }

    def __init__(self, allow_empty=False, value_field=None, **kwargs):
        self.allow_empty = allow_empty
        self.value_field = value_field
        super(DictField, self).__init__(**kwargs)

    def validate_dict(self, value):
        if not value:
            if self.allow_empty:
                return
            else:
                raise ValidationError(self.error_messages['empty'].format(value=value))

        if not isinstance(value, dict):
            raise ValidationError(self.error_messages['type'].format(vtype=type(value)))

    def convert_dict(self, value):
        if not value:
            return {}
        return value


class NumberField(BaseField):

    error_messages = {
        'min_value': 'The value {value} is smaller than min value {min_value}',
        'max_value': 'The value {value} is larger than max value {max_value}',
    }

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super(NumberField, self).__init__(**kwargs)

    def validate_range(self, value):
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(self.error_messages['min_value'].format(value=value, min_value=self.min_value))
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(self.error_messages['max_value'].format(value=value, max_value=self.max_value))


class IntegerField(NumberField):


    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)

    def convert_int(self, value):
        return int(str(value))

class FloatField(NumberField):

    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)

    def convert_float(self, value):
        return float(value)

class StringField(BaseField):

    error_messages = {
        'min_len': 'The value is shorter than min length.',
        'max_len': 'The value is longer than max length.',
        'not_allow_blank': 'The value is not allowed to be blank.'
    }

    def __init__(self, allow_blank=False, min_length=None, max_length=None, *args, **kwargs):
        self.allow_blank = allow_blank
        self.max_length = max_length
        self.min_length = min_length
        super(StringField, self).__init__(*args, **kwargs)

    def validate_len(self, value):
        if self.allow_blank:
            if len(value) == 0:
                return
        else:
            if len(value) == 0:
                raise ValidationError(self.error_messages['not_allow_blank'])

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(self.error_messages['min_len'])
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(self.error_messages['max_len'])

    def convert_str(self, value):
        if value in (None, ''):
            return u''
        if isinstance(value, unicode):
            return value
        else:
            try:
                return unicode(str(value), 'utf-8')
            except:
                return value


class SplitField(BaseField):
    error_messages = {
        'min_len': 'The value is shorter than min length.',
        'max_len': 'The value is longer than max length.',
        'not_allow_empty': 'The value is not allowed to be empty.'
    }

    def __init__(self,
                 allow_empty=True,
                 min_length=None,
                 max_length=None,
                 separator=",",
                 strip=False,
                 with_empty=False,
                 *args, **kwargs):
        self.allow_empty = allow_empty
        self.max_length = max_length
        self.min_length = min_length
        self.separator = separator
        self.strip = strip
        self.with_empty = with_empty
        super(SplitField, self).__init__(*args, **kwargs)

    def validate_len(self, value):
        if self.allow_empty:
            if len(value) == 0:
                return
        else:
            if len(value) == 0:
                raise ValidationError(self.error_messages['not_allow_empty'])

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(self.error_messages['min_len'])
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(self.error_messages['max_len'])

    def convert_str(self, value):
        if value in (None, ''):
            return []
        else:
            value = value.split(self.separator)
            if self.strip:
                value = [v.strip() for v in value]
            if not self.with_empty:
                value = [v for v in value if v]
            return value

    def validate(self, value):
        for validator in self.validators:
            validator(value)

    def load(self, value):
        if hasattr(self, 'converter') and callable(self.converter):
            value = self.converter(value)
        self.validate(value)
        return value

    def dump(self, value):
        self.validate(value)
        if not isinstance(value, (list, tuple)):
            value = [value]
        return self.separator.join(value)


class BooleanField(BaseField):

    TRUE_KEYS = ['true', '1', 'yes', 'on']
    FALSE_KEYS = ['false', '-1', '0', 'no', 'off']

    def __init__(self, true_keys=None, false_keys=None, *args, **kwargs):
        if true_keys:
            self.true_keys = true_keys
        else:
            self.true_keys = self.TRUE_KEYS
        if false_keys:
            self.false_keys = false_keys
        else:
            self.false_keys = self.FALSE_KEYS
        super(BooleanField, self).__init__(*args, **kwargs)

    def convert_boolean(self, value):
        value = str(value).lower()
        if value in self.true_keys:
            return True
        elif value in self.false_keys:
            return False
        else:
            raise ValueError

    def dump(self, value):
        value = super(BooleanField, self).dump(value)
        if value:
            return self.true_keys[0]
        else:
            return self.false_keys[0]


class IPv4Field(StringField):

    error_messages = {
        'ip_invalid': 'invalid ip address: {ip_address}'
    }

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'min_length': 7,
            'max_length': 15,
        })
        super(IPv4Field, self).__init__(*args, **kwargs)

    def validate_ip(self, value):
        ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
        if not ipv4_re.match(str(value)):
            raise ValidationError(self.error_messages['ip_invalid'].format(ip_address=value))

class PortField(IntegerField):

    error_messages = {
        'port_invalid': 'invalid port: {port}'
    }

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'min_value': 0,
            'max_value': 65535
        })
        super(PortField, self).__init__(*args, **kwargs)

    def validate_range(self, value):
        try:
            super(PortField, self).validate_range(value)
        except:
            raise ValidationError(self.error_messages['port_invalid'].format(port=value))

class URLField(StringField):

    error_messages = {
        'url_invalid': 'invalid url: {url}',
    }
    schemes = ['http', 'https', 'ftp', 'ftps', 'tcp', 'udp']

    def __init__(self, schemes=None, *args, **kwargs):
        self.schemes.extend(schemes or [])
        super(URLField, self).__init__(*args, **kwargs)

    def validate_url(self, value):
        regex = re.compile(
            r'^(?:[a-z0-9\.\-]*)://'  # scheme is validated separately
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        scheme = value.split('://')[0].lower()
        if scheme not in self.schemes:
            raise ValidationError(self.error_messages['url_invalid'].format(url=value))

        if not regex.match(value):
            raise ValidationError(self.error_messages['url_invalid'].format(url=value))

class FilePathField(StringField):

    error_messages = {
        'file_not_exists': 'file does not exists:{filepath}',
        'dir_not_exists': 'directory does not exists:{filepath}',
        'not_exists': 'file or directory not exists:{filepath}',
        'format_error': 'file or dirrectory format error: {filepath}',
    }
    path_pattern = re.compile(r'^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))')

    def __init__(self, force_check=False, parse_abs=False, *args, **kwargs):
        self.force_check = force_check
        self.parse_abs = parse_abs
        super(FilePathField, self).__init__(*args, **kwargs)

    def validate_format(self, value):
        if not self.force_check:
            if not self.path_pattern.match(value):
                raise ValidationError(self.error_messages['format_error'].format(filepath=value))
            else:
                return

    def validate_exists(self, value):
        if not self.force_check:
            return
        if isdir(value):
            if not path_exists(value):
                raise ValidationError(self.error_messages['dir_not_exists'].format(filepath=value))
        elif isfile(value):
            if not path_exists(value):
                raise ValidationError(self.error_messages['file_not_exists'].format(filepath=value))
        else:
            raise ValidationError(self.error_messages['not_exists'].format(filepath=value))

    def load(self, value):
        super(FilePathField, self).validate(value)
        value = os.path.normpath(value)
        if self.parse_abs:
            value = os.path.abspath(value)
        return value


class CompoundField(BaseField):

    error_messages = {
        'unit_invalid': 'unit {unit} is invalid, must in {units}',
        'key_miss': 'key miss, unit_key or value_key'
    }

    def __init__(self, unit_key='@unit', value_key='#text', *args, **kwargs):
        super(CompoundField, self).__init__(*args, **kwargs)
        if unit_key is None or value_key is None:
            raise FieldError(self.error_messages['key_miss'])
        self.unit_key = unit_key
        self.value_key = value_key

    def load(self, value_dict):
        if self.unit_key not in value_dict or self.value_key not in value_dict:
            raise ValidationError(self.error_messages['key_miss'])
        value = value_dict.get(self.value_key)
        unit = value_dict.get(self.unit_key)
        super(CompoundField, self).validate(value)

        if self.get_unit(unit) not in self.units:
            raise ValidationError(self.error_messages['unit_invalid'].format(unit=unit, units=self.units.keys()))
        return self.converter(value) * self.units[self.get_unit(unit)]

    def dump(self, value):
        super(CompoundField, self).validate(value)
        value, unit = self.dump_value(value)
        return {
            self.unit_key: unit,
            self.value_key: str(value)
        }


class TimeSpanField(CompoundField, FloatField):
    units = {
        "second"      : 1,
        "minute"      : 60,
        "hour"        : 60*60,
        "day"         : 24*60*60,
    }

    def __init__(self, *args, **kwargs):
        min_value = kwargs.get('min_value', None)
        if min_value is None:
            kwargs['min_value'] = 0
        super(TimeSpanField, self).__init__(*args, **kwargs)

    def dump_value(self, value):
        if value > 60 and value % 60 != 0:
            return value, 'second'
        if value%(24*3600) == 0:
            ret, unit = value/(24*3600), 'day'
        elif value%3600 == 0:
            ret, unit = value/3600, 'hour'
        elif value < 60:
            ret, unit = value, 'second'
        elif value < 3600:
            ret, unit = value/60, 'minute'
        if float(ret).is_integer():
            ret = int(ret)
        return ret, unit

    def get_unit(self, unit):
        return unit.lower()


class VolumeField(CompoundField, FloatField):
    units = {
        "B":  1,
        "KB": 1 << 10,
        "MB": 1 << 20,
        "GB": 1 << 30,
        "TB": 1 << 40,
        "PB": 1 << 50,
    }

    def __init__(self, *args, **kwargs):
        min_value = kwargs.get('min_value', None)
        if min_value is None:
            kwargs['min_value'] = 0
        super(VolumeField, self).__init__(*args, **kwargs)

    def load(self, value):
        return int(super(VolumeField, self).load(value))

    def dump_value(self, value):
        h_value, h_unit = humanize_bytes(value).split()
        h_value = float(h_value)

        if int(h_value * self.units[h_unit]) == value:
            if h_value.is_integer():
                h_value = int(h_value)
        else:
            h_value, h_unit = value, 'B'
        return h_value, h_unit

    def get_unit(self, unit):
        return unit.upper()

class ChoiceField(BaseField):

    error_messages = {
        'choice_invalid': 'Select a valid choice. {value} is not one of the available choices.',
    }

    def __init__(self, choices=None, *args, **kwargs):
        self.choices = choices or []
        super(ChoiceField, self).__init__(*args, **kwargs)

    def _find_exists(self, value):
        if value not in self.choices:
            return False
        return True

    def validate_value(self, value):
        if not self._find_exists(value):
            raise ValidationError(self.error_messages['choice_invalid'].format(value=value))


class MultipleChoiceField(ChoiceField):

    error_messages = {
        'choice_invalid': 'Select a valid choice. {value} is not one of the available choices.',
        'list_invalid': 'values must be a list.',
    }

    def validate_value(self, values):
        if len(values) == 0:
            raise ValidationError(self.error_messages['choice_invalid'].format(value=values))
        for value in values:
            if not self._find_exists(value):
                raise ValidationError(self.error_messages['choice_invalid'].format(value=value))

    def convert_list(self, values):
        if not isinstance(values, (list, tuple)):
            raise ValidationError(self.error_messages['list_invalid'])
        return values

class ExpressionField(StringField):

    error_messages = {
        'compile_error': 'expression < {expr} > compile error',
    }

    def validate_expression(self, value):
        try:
            compile(value, '<string>', 'eval')
        except (SyntaxError, TypeError):
            raise ValidationError(self.error_messages['compile_error'].format(expr=value))

class ValueField(BaseField):

    error_messages = {
        'value_invalid': 'value {value} is invalid or key {field_name} is not in value.'
    }

    def __init__(self, field_name="#text", field=None, *args, **kwargs):
        self._field_name = field_name
        if field is None:
            self._field = StringField()
        else:
            self._field = field
        super(ValueField, self).__init__(*args, **kwargs)

    def validate_value(self, value):
        return self._field.validate(value)

    def convert_value(self, value):
        try:
            v = value[self._field_name]
        except:
            raise ValidationError(self.error_messages['value_invalid'].format(value=value, field_name=self._field_name))
        return self._field.load(v)

    def dump(self, value):
        v = self._field.dump(value)
        return {
            self._field_name: v
        }

class JSONField(BaseField):

    error_messages = {
        'parse_error': 'parse json value error.',
        'unparse_error': 'unparse json value error.',
        'type_error': 'json type error.',
    }

    def __init__(self, json_type=None, *args, **kwargs):
        self._type = json_type
        super(JSONField, self).__init__(*args, **kwargs)

    def validate_json(self, value):
        if self._type == 'list':
            if not isinstance(value, list):
                raise ValidationError(self.error_messages['type_error'].format(value=value, type=self._type))
        elif self._type == 'dict':
            if not isinstance(value, dict):
                raise ValidationError(self.error_messages['type_error'].format(value=value, type=self._type))
        elif self._type == 'string':
            if not isinstance(value, basestring):
                raise ValidationError(self.error_messages['type_error'].format(value=value, type=self._type))
        elif self._type == 'null':
            if not value is None:
                raise ValidationError(self.error_messages['type_error'].format(value=value, type=self._type))

    def convert_json(self, value):
        try:
            return json.loads(value)
        except:
            raise ValidationError(self.error_messages['parse_error'].format(value=value))

    def dump(self, value):
        self.validate_json(value)
        try:
            return json.dumps(value)
        except:
            raise ValidationError(self.error_messages['unparse_error'].format(value=value))

class OrField(BaseField):

    def __init__(self, fields, **serializer_context):
        self._fields = fields
        self._serializer_context = serializer_context
        super(OrField, self).__init__()

    def load(self, value):
        from .serializers import SerializerFactory
        for i, field in enumerate(self._fields):
            serializer = SerializerFactory.create(None, field, **self._serializer_context)
            result = serializer.load(value)
            if not serializer.errors:
                return result
            else:
                if i + 1 == len(self._fields):
                    raise ValidationError(serializer.errors)
                else:
                    continue

    def validate(self, value):
        from .serializers import SerializerFactory
        for i, field in enumerate(self._fields):
            serializer = SerializerFactory.create(None, field, **self._serializer_context)
            result = serializer.validate(value)
            if not serializer.errors:
                return result
            else:
                if i + 1 == len(self._fields):
                    raise ValidationError(serializer.errors)
                else:
                    continue

    def dump(self, value):
        from .serializers import SerializerFactory
        for i, field in enumerate(self._fields):
            serializer = SerializerFactory.create(None, field, **self._serializer_context)
            result = serializer.dump(value)
            if not serializer.errors:
                return result
            else:
                if i + 1 == len(self._fields):
                    raise ValidationError(serializer.errors)
                else:
                    continue


class CommonFields(object):

    fields = {}

    def __init__(self, fields=None):
        if fields is not None:
            self.fields = fields

    def __call__(self, constructor=None):
        if constructor:
            return constructor(copy.deepcopy(self.fields))
        else:
            return self.__class__(copy.deepcopy(self.fields))

    def validate(self, data):
        return

    def load(self, data):
        return data

    def dump(self, data):
        return data


class ItemField(object):

    def __init__(self, value):
        self.value = value
