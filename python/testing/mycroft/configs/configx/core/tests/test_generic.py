#encoding=utf-8
from django.test import TestCase
from configx.core.fields import FieldName, IntegerField, StringField
from configx.core.exceptions import ValidationError
from configx.core.generic import BaseConfig, ReadWriteConfig
from configx.core.loader import MemFileLoader
from mock import Mock


class SimpleTestConfig(BaseConfig):
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
    loader_class = Mock()


class BaseConfigTest(TestCase):

    def test_load(self):
        raw_data = {
            "@version": "3.0",
            "server": {
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        config = SimpleTestConfig(raw_data=raw_data)
        self.assertEqual(config._data, {
            "version": "3.0",
            "servers": ({
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            },)
        })

        raw_data = {
            "type": "xml",
            "@version": "3.0",
            "server": {
                "id": "DS1",
                "@type": "main",
                "host": "127.0.0.1",
                "port": '80'
            }
        }
        with self.assertRaises(ValidationError):
            SimpleTestConfig(raw_data=raw_data)

    def test_dump(self):
        data = {
            "version": "3.0",
            "servers": [{
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        }
        config = SimpleTestConfig(data=data)
        self.assertEqual(config.dump(data), {
            "@version": "3.0",
            "server": [{
                "@type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        })

        data = {
            "version": "3.0",
            "servers": [{
                "id": "DS1",
                "type": "main",
                "host": "127.0.0.1",
                "port": 80
            }]
        }
        with self.assertRaises(ValidationError):
            SimpleTestConfig(data=data)

mem = {}

class Config1(ReadWriteConfig):

    config_file = "a"
    loader_class = MemFileLoader.build(mem=mem)
    fields = {
        FieldName("version", alias="@version"): StringField(),
    }


class GenericConfigTest(TestCase):

    def test_base(self):
        with self.assertRaises(ValidationError):
            Config1()
        config = Config1.make({
            "version": "0.0.1"
        })

        self.assertEquals(config.data, {
            "version": "0.0.1"
        })

        config.save()

        new_config = Config1()

        self.assertEquals(new_config.data, {
            "version": "0.0.1"
        })
        new_config.data.version = "0.0.2"

        self.assertEquals(new_config.data, {
            "version": "0.0.1"
        })

        self.assertEquals(new_config.data, config.data)


        new_config.update({
            "version": "0.0.2"
        })
        self.assertEquals(new_config.data, {
            "version": "0.0.2"
        })
        self.assertNotEquals(new_config.data, config.data)

        new_config.save()

        config = Config1()
        self.assertEquals(new_config.data, config.data)
