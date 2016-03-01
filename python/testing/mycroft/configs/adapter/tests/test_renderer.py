#encoding=utf-8
import os
from django.test import TestCase
from django.conf import settings
from adapter.renderer import (
    DataCSVRenderer,
    DataXMLRenderer,
    DataTemplateRenderer,
)

class RendererTest(TestCase):

    def test_csv_render(self):
        renderer = DataCSVRenderer()
        self.assertEquals(renderer.render({
            "a": "v",
            "c": "d"
        }, fields=["a", "c"]), "a,c\r\nv,d\r\n")

        self.assertEquals(renderer.render({
            "a": "v",
            "c": "d"
        }, fields=["a", "c"], header=False), "v,d\r\n")

        self.assertEquals(renderer.render([{
            "a": "v",
            "c": u"测试"
        },{
            "a": "g",
            "c": "编码"
        }], fields=["a", "c"], header=False), u"v,测试\r\ng,编码\r\n")


    def test_xml_render(self):
        renderer = DataXMLRenderer()
        self.assertEquals(renderer.render({
            "result": {
                "record": [
                    {"列1": "x"},
                    {u"列1": "值1"},
                    {"g": {
                        "列3": u"值2"
                    }},
                ]
            }
        }, indent=0).replace('\n', ''), '<?xml version="1.0" encoding="utf-8"?><result><record><列1>x</列1></record><record><列1>值1</列1></record><record><g><列3>值2</列3></g></record></result>'.decode("utf-8"))

    def get_template(self, name):
        root = os.path.join(settings.PROJECT_ROOT, "fixture", "adapter", "renderer")
        return os.path.abspath(os.path.join(root, name))

    def test_template_render(self):
        renderer = DataTemplateRenderer()
        self.assertEquals(renderer.render({
            "result": [
                {"a": u"值1"},
                {"a": "值2"},
                {"a": "3"}
            ]
        }, template=self.get_template("template1.xml")), '<?xml version="1.0" encoding="UTF-8"?>\n<result>\n  <a>测试</a>\n  \n  <a>值1</a>\n  \n  <a>值2</a>\n  \n  <a>3</a>\n  \n</result>'.decode("utf-8"))