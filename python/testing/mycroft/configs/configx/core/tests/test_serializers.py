#encoding=utf-8
from django.test import TestCase
from configx.core.fields import FieldName, IntegerField, StringField
from configx.core.serializers import SerializerFactory


class SerializerTest(TestCase):

    def test_basic(self):
        fields = {
            FieldName("version", alias="@version"): StringField(),
            FieldName("servers", alias="server"): [
                {
                    FieldName("type", alias="@type"): StringField(),
                    "host": StringField(),
                    "port": IntegerField()
                }
            ]
        }
        serializer = SerializerFactory.create(None, fields, error_strict=True)
        raw_data = {
            "@version": "3.0",
            "server": {
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        data = {
            "version": "3.0",
            "servers": [
                {
                    "type": "main",
                    "host": "127.0.0.1",
                    "port": 80
                }
            ]
        }
        load_data = serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(load_data, data)

        dump_data = serializer.dump(data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(dump_data, {
            "@version": "3.0",
            "server": [{
                "@type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        })


    def test_error(self):
        fields = {
            FieldName("version", alias="@version"): StringField(),
            FieldName("servers", alias="server"): [
                {
                    FieldName("type", alias="@type"): StringField(),
                    "host": StringField(),
                    "port": IntegerField()
                }
            ]
        }
        serializer = SerializerFactory.create(None, fields, error_strict=True)

        raw_data = {
            "@version": "3.0",
            "server": {
                "id": "DS1",
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 1)

        raw_data = {
            "@version": "3.0",
            "server": {
                "type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        serializer.load(raw_data)
        print serializer.errors
        self.assertEqual(len(serializer.errors), 2)


        data = {
            "version": "3.0",
            "servers": [
                {
                    "id": "DS1",
                    "type": "main",
                    "host": "127.0.0.1",
                    "port": 80
                }
            ]
        }

        serializer.dump(data)
        self.assertEqual(len(serializer.errors), 1)

    def test_optional(self):
        fields = {
            FieldName("version", alias="@version"): StringField(),
            FieldName("servers", alias="server"): [
                {
                    FieldName("id", alias="@id", optional=True): StringField(),
                    FieldName("type", alias="@type"): StringField(),
                    "host": StringField(),
                    "port": IntegerField()
                }
            ]
        }
        serializer = SerializerFactory.create(None, fields, error_strict=True)

        raw_data = {
            "@version": "3.0",
            "server": {
                "@id": "DS1",
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        load_data = serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(load_data, {
            "version": "3.0",
            "servers": [{
                "id": "DS1",
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        })

        raw_data = {
            "@version": "3.0",
            "server": {
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        load_data = serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(load_data, {
            "version": "3.0",
            "servers": [{
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        })


        data = {
            "version": "3.0",
            "servers": [
                {
                    "type": "main",
                    "host": "127.0.0.1",
                    "port": 80
                }
            ]
        }

        dump_data = serializer.dump(data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(dump_data, {
            "@version": "3.0",
            "server": [
                {
                    "@type": "main",
                    "host": "127.0.0.1",
                    "port": 80
                }
            ]
        })


    def test_error_strict(self):
        fields = {
            FieldName("version", alias="@version"): StringField(),
            FieldName("servers", alias="server"): [
                {
                    FieldName("type", alias="@type"): StringField(),
                    "host": StringField(),
                    "port": IntegerField()
                }
            ]
        }
        serializer = SerializerFactory.create(None, fields, error_strict=False)

        raw_data = {
            "@version": "3.0",
            "server": {
                "id": "main",
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        load_data = serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(load_data, {
            "version": "3.0",
            "servers": [{
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        })

    def test_list_multi(self):
        fields = {
            FieldName("version", alias="@version"): StringField(),
            FieldName("servers", alias="server"): [
                {
                    FieldName("type", alias="@type"): StringField(),
                    "host": StringField(),
                    "port": IntegerField()
                },
                {
                    FieldName("type", alias="@type"): StringField(),
                    FieldName("id", alias="@id"): StringField(),
                }
            ]
        }
        serializer = SerializerFactory.create(None, fields, error_strict=True)

        raw_data = {
            "@version": "3.0",
            "server": {
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        load_data = serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(load_data, {
            "version": "3.0",
            "servers": [{
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        })

        raw_data = {
            "@version": "3.0",
            "server": {
                "@id": "DS1",
                "@type": "main",
            }
        }
        load_data = serializer.load(raw_data)
        self.assertEqual(len(serializer.errors), 0)
        self.assertEqual(load_data, {
            "version": "3.0",
            "servers": [{
                "id": "DS1",
                "type": "main",
            }]
        })
