#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
from unittest import TestCase

CASE_ROOT = os.path.abspath(os.path.dirname(__file__))
FIXTURE_ROOT = os.path.join(CASE_ROOT, 'fixtures')

from mycroft.utils.diff.difflib import XDiff

class XDiffTestCase(TestCase):

    def setUp(self):
        super(XDiffTestCase, self).setUp()

        self._xdiff = XDiff()

    def test_diff_text_to_text(self):
        expect_result = "@@ -1,4 +1,4 @@\n"\
                        "-abba\n"\
                        "+acba\n"
        self.assertEqual('',
                            self._xdiff.text_to_text('aaaa', 'aaaa').pretty_diff_console())
        self.assertEqual(expect_result,
                            self._xdiff.text_to_text('abba', 'acba').pretty_diff_console())

    def test_diff_utf8_text_to_text(self):
        expect_result = "-中国人民\n"\
                        "+中华人民"

        diff_result = self._xdiff.text_to_text('中国人民', '中华人民').pretty_diff_console()
        self.assertTrue(expect_result, diff_result)

    def test_diff_multiline_text_to_text(self):
        expect_results = "@@ -2,7 +2,8 @@\n"\
                         " aaa\n"\
                         "\n"\
                         "-bbb\n"\
                         "+cbba\n"
        diff_result = self._xdiff.text_to_text('aaaa\nbbb', 'aaaa\ncbba').pretty_diff_console()
        self.assertTrue(expect_results, diff_result)

    def test_diff_json_to_json(self):
        expect_result = """@@ -1,27 +1,27 @@
 {

-    "a": 1,
    "b": 2

+    "a": 2,
    "b": 3

 }
"""
        diff_results = self._xdiff.json_to_json({"a": 1, "b": 2}, {"a":2, "b": 3}).pretty_diff_console()
        diff_results = diff_results.replace(' ', '')
        expect_result = expect_result.replace(' ', '')
        self.assertEqual(expect_result, diff_results)

    def test_diff_jsonfile_to_jsonfile(self):
        expect_results = """@@ -11052,45 +11052,46 @@
 ",

-                "disp_name": "捕获点",

+                "disp_name": "捕获点1",


@@ -11247,42 +11247,42 @@
 e,

-                "name": "intf3",

+                "name": "intf2",


@@ -11379,58 +11379,57 @@
 ],

-        "name": "app4",
        "state": "apply"

+        "name": "app3",
        "state": "edit"


"""
        diff_results = self._xdiff.jsonfile_to_jsonfile(
                            os.path.join(FIXTURE_ROOT, 'app_datapath.json'),
                            os.path.join(FIXTURE_ROOT, 'app_datapath.json.new')
                            ).pretty_diff_console()
        diff_results = diff_results.replace(' ', '')
        expect_results = expect_results.replace(' ', '')
        self.assertEqual(expect_results, diff_results)

        expect_results = """@@-5,23+5,23@@
{

-"a":1

+"a":2


"""
        diff_results =  self._xdiff.jsonfile_to_jsonfile(
                            os.path.join(FIXTURE_ROOT, 'app_datapath_multi.json'),
                            os.path.join(FIXTURE_ROOT, 'app_datapath_multi.json.new')
                            ).pretty_diff_console()
        diff_results = diff_results.replace(' ', '')
        expect_results = expect_results.replace(' ', '')
        self.assertEqual(expect_results, diff_results)

