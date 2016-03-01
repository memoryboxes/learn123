#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import io
import os
import json
import glob
import itertools
import copy
from mycroft.utils.diff.difflib import XDiff
from .errors import AssertionJsonDiffError
from bson import json_util
from bson.objectid import ObjectId

class DatabaseSuite(object):

    def __init__(self, datastore, db_path):
        """ init db:[colls] trees by db_file_path

        Args:
            datastore: DataStore object
            db_file_path: your fixture db file path

            for exp: fixture/test_alert/db
                     fixture|
                            |-test_alert|
                            |           |-db|
                            |               |-bpc|
                                                 |-main_app_datapath.json

            DatabaseSuite will scan `fixture/test_alert/db` and gen db config such as:
            [
                {'database':bpc, collections:
                    [
                        {'name':main_app_datapath', 'file':'main_app_datapath.json'}
                        ...
                    ]
                },
                ...
            ]
        """
        self._datastore = datastore.conn
        self._db_path = db_path
        self._db_tree = []

        db_dirs = glob.iglob(os.path.join(self._db_path, '*'))
        db_dirs = (x for x in db_dirs if os.path.isdir(x))
        for db in db_dirs:
            db_item = {'database':os.path.basename(db), 'collections':[]}

            collection_dirs = glob.glob(os.path.join(self._db_path, db, '*'))
            collections = (x for x in collection_dirs if os.path.isfile(x))
            for collection in collections:
                db_item['collections'].append(
                        {'file':os.path.basename(collection),
                         'name':os.path.splitext(os.path.basename(collection))[0]})
            self._db_tree.append(db_item)

    def syncdb(self, dropfirst=False):
        """sync json file to database"""
        for db in self._db_tree:
            for collection in db['collections']:
                if dropfirst:
                    self._datastore[db['database']][collection['name']].drop()

                with io.open(os.path.join(self._db_path, db['database'],
                             collection['file']), encoding='utf-8') as coll_json:
                    for record in coll_json.readlines():
                        record = json_util.loads(record)
                        self._datastore[db['database']][collection['name']].insert(record, check_keys=False)

    def _normal_objid(self, record):
        if isinstance(record['_id'],dict) and record['_id'].has_key("$oid"):
            obj_id_str = record['_id'].get('$oid', '')
            if isinstance(obj_id_str, basestring) and len(obj_id_str) == 24:
                record['_id'] = ObjectId(obj_id_str)
        return record

    def clean(self):
        for db in self._db_tree:
            for collection in db['collections']:
                self._datastore[db['database']][collection['name']].drop()

    def assertExists(self):
        """raise AssertionError if database or collections don't exist"""
        for db in self._db_tree:
            assert(db in self._datastore.conn.database_names)
            for collection in db['collections']:
                assert(collection['name'] in self._datastore[db['database']].collection_names())

    def diff(self, exclude=[], auto_format=True, query={}):
        """raise AssertionError if collections don't match by fixtures"""
        self._exclude_keys = exclude
        for db in self._db_tree:
            for collection in db['collections']:
                db_data_content = self._datastore[db['database']][collection['name']].find(query)
                db_file_content = file(os.path.join(self._db_path,
                                       db['database'], collection['file']), 'r').readlines()
                for record, line in itertools.izip_longest(db_data_content, db_file_content, fillvalue={}):
                    remote_db_record = self._stripkey(self._stripoid(record), self._exclude_keys)
                    local_file_record = self._stripkey(self._stripoid(json.loads(line)),self._exclude_keys)
                    if auto_format:
                        remote_db_record = self._formatvalue(remote_db_record)
                        local_file_record = self._formatvalue(local_file_record)
                    if remote_db_record != local_file_record:
                        raise AssertionJsonDiffError(
                                XDiff().json_to_json(remote_db_record,
                                                     local_file_record).pretty_diff_console()
                            )

    def diffdisorder(self, exclude=[], auto_format=True, query={}):
        self._exclude_keys = exclude
        for db in self._db_tree:
            for collection in db['collections']:
                db_data_content = self._datastore[db['database']][collection['name']].find(query)
                db_file_content = file(os.path.join(self._db_path,
                                       db['database'], collection['file']), 'r').readlines()
                if db_data_content.count() != len(db_file_content):
                    raise AssertionJsonDiffError("The datas in file and db are not the same length")

                for file_content in range(len(db_file_content)):
                    db_file_content[file_content] = self._stripkey(self._stripoid(json.loads(db_file_content[file_content])), self._exclude_keys)
                    if auto_format:
                        db_file_content[file_content] = self._formatvalue(db_file_content[file_content])

                for data_content in db_data_content:
                    self._stripkey(self._stripoid(data_content), self._exclude_keys)
                    if auto_format:
                        data_content = self._formatvalue(data_content)
                    if data_content not in db_file_content:
                        raise AssertionJsonDiffError(json.dumps(data_content, ensure_ascii=False, sort_keys=True, indent=4, encoding='utf-8'))

    @property
    def datastore(self):
        return self._datastore

    def _stripoid(self, json_obj):
        if json_obj.get('_id', None) != None:
            del json_obj['_id']
        return json_obj

    def _stripkey(self, json_obj, keys):
        if not isinstance(json_obj, dict):
            return json_obj

        for key in keys:
            if json_obj.get(key,None) != None:
                del json_obj[key]
        for key, value in json_obj.iteritems():
            if isinstance(value, dict):
                self._stripkey(value, keys)
            elif isinstance(value, list):
                for item in value:
                    self._stripkey(item, keys)
        return json_obj

    def _formatvalue(self, json_obj):
        if not isinstance(json_obj, dict):
            return json_obj

        for key, value in json_obj.iteritems():
            if type(value) == float:
                json_obj[key] = round(value, 2)
            elif isinstance(value, dict):
                self._formatvalue(value)
            elif isinstance(value, list):
                for item in value:
                    self._formatvalue(item)
        return json_obj

