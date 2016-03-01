#encoding=utf-8
from .fields import BaseField, FieldName, CommonFields, ItemField
from .exceptions import ValidationError, NON_FIELD_ERRORS
from .utils import undefined



def cascade_field_name(*args):
    parts = []
    for arg in args:
        if arg is not None:
            parts.append(str(arg))
    return ".".join(parts)


def catch_add_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ValidationError as e:
            self.add_error(None, e)
            return undefined
    return wrapper

def reset_errors(func):
    def wrapper(self, *args, **kwargs):
        self._errors = {}
        self._wrong_key_errors = {}
        return func(self, *args, **kwargs)
    return wrapper


class SerializerFactory(object):

    @staticmethod
    def create(name, field, **kwargs):
        if isinstance(field, BaseField):
            return FieldSerializer(name, field, **kwargs)
        elif isinstance(field, CommonFields):
            return CommonFieldsSerializer(name, field, **kwargs)
        elif isinstance(field, ItemField):
            return ItemFieldSerializer(name, field, **kwargs)
        elif isinstance(field, dict):
            return DictSerializer(name, field, **kwargs)
        elif isinstance(field, list):
            return ListSerializer(name, field, **kwargs)
        elif isinstance(field, tuple):
            return TupleSerializer(name, field, **kwargs)


class BaseSerializer(object):

    def __init__(self, field_name, *args, **kwargs):
        self._field_name = field_name
        self._context = {
            "error_strict": kwargs.pop("error_strict", True),
            "dict_constructor": kwargs.pop("dict_constructor", dict),
        }
        self._errors = {}
        self._wrong_key_errors = {}
        self.initial(*args, **kwargs)

    @property
    def field_name(self):
        return self._field_name

    @property
    def errors(self):
        errors = dict(self._errors)
        if self._context["error_strict"]:
            errors.update(self._wrong_key_errors)
        return errors

    def validate(self, value):
        raise NotImplementedError()

    def load(self, raw_value):
        raise NotImplementedError()

    def dump(self, value):
        raise NotImplementedError()

    def add_error(self, field_name, error):
        if not field_name:
            error_field = self._field_name
        else:
            error_field = field_name
        if error_field in self._errors:
            error = ValidationError([self._errors[error_field], error])
        self._errors[error_field] = error

    def add_wrong_key_error(self, field_name, error):
        if not field_name:
            error_field = self._field_name
        else:
            error_field = field_name
        if error_field in self._wrong_key_errors:
            error = ValidationError([self._wrong_key_errors[error_field], error])
        self._wrong_key_errors[error_field] = error



class FieldSerializer(BaseSerializer):

    def initial(self, field):
        self._field = field

    @catch_add_error
    @reset_errors
    def load(self, raw_value):
        return self._field.load(raw_value)

    @catch_add_error
    @reset_errors
    def validate(self, value):
        return self._field.validate(value)

    @catch_add_error
    @reset_errors
    def dump(self, value):
        return self._field.dump(value)


class DictSerializer(BaseSerializer):

    def initial(self, schema):
        self._schema = schema

    @catch_add_error
    @reset_errors
    def load(self, raw_value):
        if not isinstance(raw_value, dict):
            self.add_error(None, ValidationError('DictField value type should be dict'))
            return

        alias_raw_value = type(raw_value)(raw_value)
        wrong_keys = set()
        for k in self._schema.iterkeys():
            if isinstance(k, FieldName) and k.alias:
                if str(k) in alias_raw_value:
                    alias_raw_value.pop(str(k))
                    wrong_keys.add(str(k))
                if k.alias in alias_raw_value:
                    alias_raw_value[k] = alias_raw_value.pop(k.alias)

        if wrong_keys:
            top_full_name = cascade_field_name(self._field_name, NON_FIELD_ERRORS)
            self.add_wrong_key_error(top_full_name, ValidationError('wrong_keys %s' % wrong_keys))
        return self._do_action(alias_raw_value, "load")

    @catch_add_error
    @reset_errors
    def dump(self, value):
        value = self._do_action(value, "dump")

        alias_value = type(value)(value)
        for k in self._schema.iterkeys():
            if isinstance(k, FieldName) and k.alias:
                if str(k) in alias_value:
                    alias_value[k.alias] = alias_value.pop(str(k))

        return alias_value

    @catch_add_error
    @reset_errors
    def validate(self, value):
        return self._do_action(value, "validate")

    def _do_action(self, value, action):
        if not isinstance(value, dict):
            self.add_error(None, ValidationError('DictField value type should be dict'))
            return

        schema_keys = [str(key) for key in self._schema.iterkeys()]
        wrong_keys = set(value.keys()) - set(schema_keys)
        if wrong_keys:
            top_full_name = cascade_field_name(self._field_name, NON_FIELD_ERRORS)
            self.add_wrong_key_error(top_full_name, ValidationError('wrong_keys %s' % wrong_keys))

        convert_values = self._context["dict_constructor"]()
        for sub_name, sub_field in self._schema.iteritems():
            sub_full_name = cascade_field_name(self._field_name, sub_name)
            sub_value = value.get(str(sub_name), getattr(sub_name, "default", undefined))
            if sub_value is undefined:
                if isinstance(sub_name, FieldName) and sub_name.optional:
                    continue
                else:
                    self.add_error(sub_full_name, ValidationError("field is missing"))
            else:
                serializer = SerializerFactory.create(sub_full_name, sub_field, **self._context)
                sub_action_value = getattr(serializer, action)(sub_value)
                if sub_action_value is not undefined:
                    convert_values[str(sub_name)] = sub_action_value

                for error_field, error in serializer.errors.iteritems():
                    self.add_error(error_field, error)
        return convert_values


class ListSerializer(BaseSerializer):

    def initial(self, schemas):
        self._schemas = schemas

    @catch_add_error
    @reset_errors
    def load(self, raw_value):
        if not isinstance(raw_value, (list, tuple)):
            raw_value = [raw_value]
        return self._do_action(raw_value, "load")

    @catch_add_error
    @reset_errors
    def dump(self, value):
        return self._do_action(value, "dump")

    @catch_add_error
    @reset_errors
    def validate(self, value):
        return self._do_action(value, "validate")

    def _do_action(self, value, action):
        if not isinstance(value, (list, tuple)):
            self.add_error(None, ValidationError("ListField value type should be list/tuple"))
            return

        convert_values = []
        for i, item_value in enumerate(value):
            item_full_name = cascade_field_name(self._field_name, i)
            cached_errors = []
            for schema in self._schemas:
                serializer = SerializerFactory.create(item_full_name, schema, **self._context)
                item_action_value = getattr(serializer, action)(item_value)
                if not serializer.errors:
                    convert_values.append(item_action_value)
                    break
                else:
                    cached_errors.append(serializer.errors)
            else:
                if len(self._schemas) == 1 and cached_errors:
                    for error_field, error in cached_errors[0].iteritems():
                        self.add_error(error_field, error)
                else:
                    self.add_error(item_full_name, ValidationError('ListField value not have matched schema'))
        return convert_values


class TupleSerializer(BaseSerializer):

    def initial(self, schemas):
        self._schemas = schemas

    @catch_add_error
    @reset_errors
    def load(self, raw_value):
        return self._do_action(raw_value, "load")

    @catch_add_error
    @reset_errors
    def dump(self, value):
        return self._do_action(value, "dump")

    @catch_add_error
    @reset_errors
    def validate(self, value):
        return self._do_action(value, "validate")

    def _do_action(self, value, action):
        convert_value = undefined
        full_name = cascade_field_name(self._field_name, NON_FIELD_ERRORS)
        cached_errors = []
        for schema in self._schemas:
            serializer = SerializerFactory.create(self._field_name, schema, **self._context)
            action_value = getattr(serializer, action)(value)
            if not serializer.errors:
                convert_value = action_value
                break
            else:
                cached_errors.append(serializer.errors)
        else:
            if len(self._schemas) == 1 and cached_errors:
                for error_field, error in cached_errors[0].iteritems():
                    self.add_error(error_field, error)
            else:
                self.add_error(full_name, ValidationError('OrChoiceField value not have matched schema'))
        return convert_value


class CommonFieldsSerializer(BaseSerializer):

    def get_serializer_context(self):
        return {
            "error_strict": True,
            "dict_constructor": dict,
        }

    def initial(self, field):
        self.field = field
        self.serializer = SerializerFactory.create(None, field.fields, **self.get_serializer_context())

    @catch_add_error
    @reset_errors
    def load(self, raw_value):
        value = self.serializer.load(raw_value)
        if self.serializer.errors:
            for error_field, error in self.serializer.errors.iteritems():
                self.add_error(error_field, error)
        else:
            return self.field.load(value)

    @catch_add_error
    @reset_errors
    def dump(self, value):
        value =self.field.dump(value)
        if self.serializer.errors:
            for error_field, error in self.serializer.errors.iteritems():
                self.add_error(error_field, error)
        else:
            return self.serializer.dump(value)

    @catch_add_error
    @reset_errors
    def validate(self, value):
        self.field.validate(value)


class ItemFieldSerializer(BaseSerializer):

    def initial(self, schema):
        self._schema = schema

    @catch_add_error
    @reset_errors
    def load(self, raw_value):
        if not isinstance(raw_value, dict):
            self.add_error(None, ValidationError('DictField value type should be dict'))
            return

        alias_raw_value = type(raw_value)(raw_value)
        return self._do_action(alias_raw_value, "load")

    @catch_add_error
    @reset_errors
    def dump(self, value):
        value = self._do_action(value, "dump")
        alias_value = type(value)(value)
        return alias_value

    @catch_add_error
    @reset_errors
    def validate(self, value):
        return self._do_action(value, "validate")

    def _do_action(self, value, action):
        if not isinstance(value, dict):
            self.add_error(None, ValidationError('DictField value type should be dict'))
            return
        convert_values = self._context["dict_constructor"]()
        sub_field = self._schema.value
        for sub_name, sub_value in value.iteritems():
            sub_full_name = cascade_field_name(self._field_name, sub_name)
            serializer = SerializerFactory.create(sub_full_name, sub_field, **self._context)
            sub_action_value = getattr(serializer, action)(sub_value)
            if sub_action_value is not undefined:
                convert_values[str(sub_name)] = sub_action_value

            for error_field, error in serializer.errors.iteritems():
                self.add_error(error_field, error)
        return convert_values
