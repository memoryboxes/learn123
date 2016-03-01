# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from configx.core.fields import (
    IntegerField,
    FloatField,
    BooleanField,
    StringField,
    IPv4Field,
    PortField,
    URLField,
    FilePathField,
    TimeSpanField,
    VolumeField,
    ChoiceField,
    MultipleChoiceField,
    ExpressionField,
    ValueField,
    JSONField,
)
from configx.core.exceptions import (
    ValidationError,
)

class FieldsTest(TestCase):

    def test_integer(self):
        field = IntegerField(min_value=40, max_value=80)
        field.validate(40)
        field.validate(50)
        field.validate(80)
        self.assertEquals(field.load(55), 55)
        with self.assertRaises(ValidationError):
            field.validate(1)
        with self.assertRaises(ValidationError):
            field.validate('a')
        with self.assertRaises(ValidationError):
            field.dump(20)
        with self.assertRaises(ValidationError):
            field.dump('a')
        with self.assertRaises(ValidationError):
            field.load(1.23)

    def test_float(self):
        field = FloatField(min_value=0.1, max_value=10.3)
        field.validate(0.1)
        field.validate(4.5)
        field.validate(10.3)
        self.assertEquals(field.load('9.86'), 9.86)
        self.assertEquals(field.dump(9.86), 9.86)
        with self.assertRaises(ValidationError):
            field.validate(-1)
        with self.assertRaises(ValidationError):
            field.validate('a')
        with self.assertRaises(ValidationError):
            field.dump(-1)
        with self.assertRaises(ValidationError):
            field.dump('a')

    def test_boolean(self):
        field = BooleanField(false_keys=['abc'])
        self.assertTrue(field.load(1))
        self.assertTrue(field.load('1'))
        self.assertTrue(field.load('True'))
        self.assertFalse(field.load('-1'))
        self.assertFalse(field.load(0))
        self.assertFalse(field.load('off'))
        self.assertFalse(field.load('abc'))
        with self.assertRaises(ValidationError):
            field.load('100')

    def test_string(self):
        field = StringField()
        self.assertEqual(field.load('abc'), u'abc')
        with self.assertRaises(ValidationError):
            field.load('')

        field = StringField(min_length=4)
        with self.assertRaises(ValidationError):
            field.load('abc')

        field = StringField(allow_blank=True, min_length=4)
        self.assertEqual(field.load(None), u'')
        self.assertEqual(field.load('abcd'), 'abcd')
        with self.assertRaises(ValidationError):
            field.load('abc')

        field = StringField(allow_blank=True)
        self.assertEqual(field.load(None), u'')
        self.assertEqual(field.load('abcd'), u'abcd')
        self.assertEqual(field.load('abc'), u'abc')

    def test_ip(self):
        field = IPv4Field()
        self.assertTrue(field.load('127.0.0.1'))
        self.assertTrue(field.load('0.0.0.0'))
        self.assertTrue(field.load('255.255.255.255'))
        with self.assertRaises(ValidationError):
            field.load(100)

    def test_port(self):
        field = PortField()
        field.load(0)
        field.load(65535)
        with self.assertRaises(ValidationError):
            field.load(75535)
        with self.assertRaises(ValidationError):
            field.load(-1)

    def test_url(self):
        field = URLField(schemes=['zmq'])
        self.assertEquals(field.load('http://127.0.0.1:8080'), 'http://127.0.0.1:8080')
        self.assertEquals(field.load('http://127.0.0.1'), 'http://127.0.0.1')
        self.assertEquals(field.load('http://127.0.0.1?query=1'), 'http://127.0.0.1?query=1')
        self.assertEquals(field.load('zmq://127.0.0.1:8080'), 'zmq://127.0.0.1:8080')
        self.assertEquals(field.load('ftp://localhost:8080/home'), 'ftp://localhost:8080/home')

    def test_file(self):
        field = FilePathField(force_check=True)
        self.assertEquals(field.load('/home/'), '/home')
        with self.assertRaises(ValidationError):
            field.load('/xxx/yyyy')

        field = FilePathField()
        self.assertEquals(field.load('/home/'), '/home')
        self.assertEquals(field.load('/xxx/yyyy'), '/xxx/yyyy')
        # TODO
        # with self.assertRaises(ValidationError):
        #     field.load('\n')

    def test_time_span(self):
        field = TimeSpanField(unit_key="@unit", value_key="#text")
        self.assertEquals(field.load({'@unit': 'day', '#text': '2'}), 2*24*3600)
        self.assertEquals(field.load({'@unit': 'second', '#text': '0.3'}), 0.3)
        self.assertEquals(field.load({'@unit': 'minute', '#text': '0.2'}), 0.2*60)
        self.assertEquals(field.dump(2*24*3600), {'@unit': 'day', '#text': '2'})
        self.assertEquals(field.dump(2*3600), {'@unit': 'hour', '#text': '2'})
        self.assertEquals(field.dump(60*7), {'@unit': 'minute', '#text': '7'})
        self.assertEquals(field.dump(60*7+0.1), {'@unit': 'second', '#text': '420.1'})
        self.assertEquals(field.dump(56.1), {'@unit': 'second', '#text': '56.1'})
        self.assertEquals(field.dump(60+2), {'@unit': 'second', '#text': '62'})
        self.assertEquals(field.dump(2*60+2), {'@unit': 'second', '#text': '122'})
        self.assertEquals(field.dump(60*60+3), {'@unit': 'second', '#text': '3603'})
        self.assertEquals(field.dump(60*60+3.1), {'@unit': 'second', '#text': '3603.1'})

        with self.assertRaises(ValidationError):
            field.load({'@unit': 'day', '#text': ''})

        with self.assertRaises(ValidationError):
            field.load({'@unit': 'day', '#text': '-1'})


    def test_volume(self):
        field = VolumeField(unit_key="@unit", value_key="#text")
        self.assertEquals(field.load({'@unit': 'KB', '#text': '2'}), 2<<10)
        self.assertEquals(field.load({'@unit': 'KB', '#text': '0.3'}), 307)
        self.assertEquals(field.load({'@unit': 'B', '#text': '0.3'}), 0)
        self.assertEquals(field.dump(2<<20), {'@unit': 'MB', '#text': '2'})
        self.assertEquals(field.dump(3<<30), {'@unit': 'GB', '#text': '3'})
        self.assertEquals(field.dump(1024*1025), {'@unit': 'B', '#text': '1049600'})
        self.assertEquals(field.load({'@unit': 'KB', '#text': '1025'}), 1025*1024)
        self.assertEquals(field.load({'@unit': 'B', '#text': '1025'}), 1025)

        with self.assertRaises(ValidationError):
            field.load({'@unit': 'bps', '#text': '100'})


    def test_choice(self):
        field = ChoiceField(choices=['a', 'b', 'c'])
        self.assertEquals(field.load('c'), 'c')
        with self.assertRaises(ValidationError):
            field.load(3)

    def test_multi_choice(self):
        field = MultipleChoiceField(choices=['a', 'b', 'c'])
        self.assertEquals(field.load(['c']), ['c'])
        self.assertEquals(field.load(['a', 'b', 'c']), ['a', 'b', 'c'])
        with self.assertRaises(ValidationError):
            field.load(['a', 's'])
        with self.assertRaises(ValidationError):
            field.load([])
        with self.assertRaises(ValidationError):
            field.load('a')

    def test_expression(self):
        field = ExpressionField()
        self.assertEqual(field.load('2*3'), '2*3')
        self.assertEqual(field.load('2>3'), '2>3')
        self.assertEqual(field.load('"req" if getvalue("a.b.d").startswith("rd") else "resp"'), '"req" if getvalue("a.b.d").startswith("rd") else "resp"')

        with self.assertRaises(ValidationError):
            field.load('2)3')
        with self.assertRaises(ValidationError):
            field.load('if')
        with self.assertRaises(ValidationError):
            field.load('if a else b')

    def test_value(self):
        field = ValueField()
        self.assertEqual(field.load({
            '#text': 'aaa',
        }), 'aaa')

        self.assertEqual(field.dump('aaa'), {
            '#text': 'aaa'
        })

    def test_json(self):
        field = JSONField()
        self.assertEqual(field.load(json.dumps({
            '#text': 'aaa',
        })), {
            '#text': 'aaa',
        })

        self.assertEqual(field.dump('aaa'), '"aaa"')
