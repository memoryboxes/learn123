#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import csv
import glob
import json
import shutil
import operator
import itertools
import unittest
import xmltodict
import io
from .base import BaseCommand, DiffCommand
from mycroft.utils.diff.difflib import XDiff
from mycroft.core.datastore.errors import AssertionTextDiffError, AssertionJsonDiffError

class FilePutCommand(BaseCommand):

    def __init__(self, vm,
                        datastore_path,
                        remote_path):
        self._vm = vm
        self._datastore_path = datastore_path
        self._remote_path = remote_path
        super(FilePutCommand, self).__init__(
            cmd_des="put local file:{} to remote:{}".format(
                                                self._datastore_path,
                                                self._remote_path)
        )

    def execute(self):
        self._vm.putfile(self._datastore_path,
                        self._remote_path)


class FileGetCommand(BaseCommand):

    def __init__(self, vm,
                        datastore_path,
                        remote_path):
        self._vm = vm
        self._remote_path = remote_path
        self._datastore_path = datastore_path
        super(FileGetCommand, self).__init__(
            cmd_des="get remote file:{} to local:{}".format(
                                                self._remote_path,
                                                self._datastore_path)
        )

    def execute(self):
        self._vm.getfile(self._remote_path,
                         self._datastore_path)


class FileDiffCommand(DiffCommand):

    def __init__(self, vm,
                        filetype,
                        local_path,
                        remote_path,
                        exclude,
                        cmd_des="file diff object construct"):
        self._vm = vm
        self._filetype = filetype
        self._remote_path = remote_path
        self._local_path = local_path
        self._exclude = exclude
        super(FileDiffCommand, self).__init__(
            "{}, remote_path:{}, local_path:{}".format(
                                                cmd_des,
                                                self._remote_path,
                                                self._local_path)
        )

    def execute(self):
        pass

    def assertDiff(self):
        local_files = glob.iglob(os.path.join(self._local_path, '*'))
        remote_files = glob.iglob(os.path.join(self._remote_path, '*'))
        for local, remote in itertools.izip_longest(local_files, remote_files, fillvalue={}):
            if self._filetype == "json":
                local_json = [self._stripkey(record, self._exclude) for record in json.load(open(local, 'r'))]
                remote_json = [self._stripkey(record, self._exclude) for record in json.load(open(remote, 'r'))]
                diff = XDiff().json_to_json(self._stripkey(local_json, self._exclude), self._stripkey(remote_json, self._exclude)).pretty_diff_console()
            elif self._filetype == "text":
                diff = XDiff().text_to_text(self._stripkey(local, self._exclude), self._stripkey(remote, self._exclude)).pretty_diff_console()
            else:
                diff = XDiff().file_to_file(self._stripkey(local, self._exclude), self._stripkey(remote, self._exclude)).pretty_diff_console()

            if diff:
                self._fileclean(self._remote_path)
                print diff
                raise AssertionJsonDiffError()

        self._fileclean(self._remote_path)

    def _stripkey(self, json_obj, keys):
        if not isinstance(json_obj, dict):
            return json_obj

        for key in keys:
            if json_obj.get(key, None) != None:
                del json_obj[key]
        for key, value in json_obj.iteritems():
            if isinstance(value, dict):
                self._stripkey(value, keys)
            elif isinstance(value, list):
                for item in value:
                    self._stripkey(item, keys)
        return json_obj

    def _fileclean(self, path):
        files = os.listdir(path)
        for file in files:
            os.remove(os.path.join(path, file))
            

class FileDiffOfCSVCommand(DiffCommand):

    def __init__(self, vm,
                        local_path,
                        remote_path,
                        cmd_des="csv file diff object construct"):
        self.vm = vm
        self.remote_path = remote_path
        self.local_path = os.path.abspath(local_path)
        self.local_remote_path = os.path.join(os.path.abspath('%s/..' % self.local_path), 'remote')
        if not os.path.exists(self.local_remote_path):
            os.mkdir(self.local_remote_path)
        super(FileDiffOfCSVCommand, self).__init__(
            "{}, remote_path:{}, local_path:{}".format(
                                                cmd_des,
                                                self.remote_path,
                                                self.local_path)
        )

    def execute(self):
        FileGetCommand(self.vm, self.local_remote_path, "%s/*" % self.remote_path).execute()

    def assertDiff(self):
        local_files = glob.iglob(os.path.join(self.local_path, '*'))
        remote_files = glob.iglob(os.path.join(self.local_remote_path, '*'))
        for local, remote in itertools.izip_longest(local_files, remote_files, fillvalue={}):
            print "diff file : %s" % os.path.basename(local)
            with open(local) as local_csv:
                local_lines = sorted([line for line in local_csv.readlines()])
            with open(remote) as remote_csv:
                remote_lines = sorted([line for line in remote_csv.readlines()])
            diff = XDiff().text_to_text(''.join(local_lines), ''.join(remote_lines)).pretty_diff_console()

            if diff:
                print diff
                raise AssertionTextDiffError()

        self._fileclean()

    def _fileclean(self):
        shutil.rmtree(self.local_remote_path)


class FileDiffOfXMLCommand(DiffCommand):

    def __init__(self, local_path,
                       remote_path,
                       cmd_des = "xml file diff object construct"):
        self.remote_path = remote_path
        self.local_path = local_path
        super(FileDiffOfXMLCommand, self).__init__(cmd_des)

    def execute(self):
        pass

    def assertDiff(self):
        xmlsamed = self.xmlcompare()
        print xmlsamed
        return xmlsamed

    def xmlfiletodict(self,filepath):
        with io.open(filepath, 'r', encoding='UTF-8') as comparedxml:
            comparedxmlcontent = comparedxml.read()
            if comparedxmlcontent != "":
                compareddict = xmltodict.parse(comparedxmlcontent)
                return compareddict

    def xmlcompare(self):
        file1paths=glob.iglob(os.path.join(self.local_path, '*'))
        xmlsamed = True
        for file1path in file1paths:
            comparedFileNames = file1path.split('/')
            filelen = len(file1path.split('/'))
            print file1path

            file1 = self.xmlfiletodict(file1path)
            if file1 == None:
                print "This file in local is empty"
                continue

            file2path = os.path.join(self.remote_path, comparedFileNames[filelen-1])

            if os.path.exists(file2path) == False:
                xmlsamed = False
                break

            file2 = self.xmlfiletodict(file2path)
            if file2 == None:
                print "The file in remote is empty"
                continue

            if XDiff().dict_diff(file1,file2):
                xmlsamed = False
                break

        return xmlsamed


class FileFolderDiffCommand(DiffCommand):

    def __init__(self, folder1_path,
                       folder2_path,
                       cmd_des = "file folder diff"):
        self.folder1_path = folder1_path
        self.folder2_path = folder2_path
        super(FileFolderDiffCommand, self).__init__(cmd_des)

    def execute(self):
        pass

    def assertDiff(self):
        list1 = os.listdir(self.folder1_path)
        list2 = os.listdir(self.folder2_path)
        list1.sort()
        list2.sort()

        if list1 != list2:
            raise Exception("The files in %s and %s are different." % (self.folder1_path, self.folder2_path))
        else:
            print "The files in %s and %s are the same." % (self.folder1_path, self.folder2_path)
