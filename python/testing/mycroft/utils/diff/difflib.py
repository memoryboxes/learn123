#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import io
import json

from .googlediff import diff_match_patch as dmp

class XDiffResult(object):

    def __init__(self, result):
        self._result = result
        self._dmp = dmp()

    def pretty_diff_console(self):
        self._dmp.diff_cleanupSemantic(self._result)
        patch = self._dmp.patch_make(self._result)
        return self._dmp.patch_toText(patch)

    def pretty_diff_html(self):
        return self._dmp.diff_prettyHtml(self._result)

class XDiff(object):

    def __init__(self, encoding='utf-8'):
        self._dmp = dmp()
        self._encoding=encoding

    def _diff_line_mode(self, textA, textB):
        if not isinstance(textA, unicode):
            textA = textA.decode(self._encoding)
        if not isinstance(textB, unicode):
            textB = textB.decode(self._encoding)

        line_textA, line_textB, line_diffs = self._dmp.diff_linesToChars(textA, textB)
        diffs = self._dmp.diff_main(line_textA, line_textB, False)
        self._dmp.diff_charsToLines(diffs, line_diffs)
        return diffs

    def text_to_text(self, textA, textB):
        return XDiffResult(self._diff_line_mode(textA, textB))

    def json_to_json(self, objA, objB):
        json_objA = json.dumps(objA, ensure_ascii=False, sort_keys=True, indent=4, encoding=self._encoding)
        json_objB = json.dumps(objB, ensure_ascii=False, sort_keys=True, indent=4, encoding=self._encoding)
        return self.text_to_text(json_objA, json_objB)

    def file_to_file(self, fileA, fileB, encoding='utf-8'):
        with io.open(fileA, 'r', encoding=encoding) as _fileA, \
             io.open(fileB, 'r', encoding=encoding) as _fileB:
                return self.text_to_text(_fileA.read(), _fileB.read())

    def __sort_jsons_file(self, file):
        _file_string = file.read()
        _file_string = _file_string.replace('\r\n', '\n').replace('\n', '')
        _bracket_num = 0
        _brace_num = 0
        _key_loc = 0
        _in_block = False
        while _key_loc != len(_file_string):
            if _file_string[_key_loc] == '[':
                _bracket_num += 1
                _key_loc += 1
                _in_block = True
                continue
            if _file_string[_key_loc] == '{':
                _brace_num += 1
                _key_loc += 1
                _in_block = True
                continue
            if _file_string[_key_loc] == ']':
                _bracket_num -= 1
            if _file_string[_key_loc] == '}':
                _brace_num -= 1
            if _in_block is True and _bracket_num == 0 and _brace_num == 0 and _key_loc != len(_file_string) - 1:
                _file_string = _file_string[:_key_loc + 1] + "^" + _file_string[_key_loc + 1:]
                _in_block = False
            _key_loc += 1

        _file_array = _file_string.split("^")
        _file_array.sort()
        _file_string = '[' + ','.join(_file_array) + ']'
        return _file_string

    def jsonfile_to_jsonfile(self, fileA, fileB):
        with io.open(fileA, 'r', encoding=self._encoding) as _fileA, \
             io.open(fileB, 'r', encoding=self._encoding) as _fileB:
                return  self.json_to_json(
                                        json.loads(self.__sort_jsons_file(_fileA), encoding=self._encoding),
                                        json.loads(self.__sort_jsons_file(_fileB), encoding=self._encoding)
                )

    def list_diff(self,l_list, r_list):
        '''
        >>> dt1 = ['a', 100, 13, 'z', 'b']
        >>> dt2 = ['b', 'a', 'z', 13, 100]
        >>> list_diff(dt1, dt2)
        False

        >>> dt1 = ['a', {"e": {"f": ['a', 'b', 'c', [3,1,2]]}}, 13, 'z', 'b']
        >>> dt2 = ['a', {"e": {"f": ['a', 'b', 'c', [3,1,2]]}}, 13, 'z', 'b']
        >>> list_diff(dt1, dt2)
        False

        >>> dt1 = ['a', {"e": {"f": ['a', 'b', 'c', [3,1,2]]}}, 13, 'z', 'b']
        >>> dt2 = ['a', {"e": {"f": ['a', 'b', 'c', [3,1,3]]}}, 13, 'z', 'b']
        >>> list_diff(dt1, dt2)
        True
        '''

        if len(l_list) != len(r_list):
            return True
        else:
            sorted_l_list = sorted(l_list)
            sorted_r_list = sorted(r_list)

            has_diff = False
            for i, lv in enumerate(sorted_l_list):
                rv = sorted_r_list[i]
                if type(lv) != type(rv):
                    has_diff = True
                    break
                else:
                    if isinstance(lv, dict):
                        has_diff = self.dict_diff(lv, rv)
                        if has_diff:
                            break
                    elif isinstance(lv, (list, tuple)):
                        has_diff = self.list_diff(lv, rv)
                        if has_diff:
                            break
                    else:
                        has_diff = lv != rv
                        if has_diff:
                            break

            return has_diff

    def dict_diff(self,left_dict, right_dict):
        '''
        >>> dt1 = {"name": "abc", "age": 20}
        >>> dt2 = {"age": 20, "name": "abc"}
        >>> dict_diff(dt1, dt2)
        False

        >>> dt1 = {"name": "abc", "hobbies": ["running", "programming"], "age": 20}
        >>> dt2 = {"hobbies": ["programming", "runnin"], "age": 20, "name": "abc"}
        >>> dict_diff(dt1, dt2)
        True

        >>> dt1 = {"name": "abc", "ex_hobbies": [{"name": "programming"}, "running", {"name": "writing", "years": 10}], "age": 20}
        >>> dt2 = {"ex_hobbies": ["running", {"name": "writing", "years": 10}, {"name": "programming"}], "age": 20, "name": "abc"}
        >>> dict_diff(dt1, dt2)
        False

        >>> dt1 = {"name": "abc", "ex_hobbies": [{"name": "programming"}, "running", {"name": "writing", "years": 10}], "age": 20}
        >>> dt2 = {"ex_hobbies": ["running", {"name": "writing", "years": 20}, {"name": "programming"}], "age": 20, "name": "abc"}
        >>> dict_diff(dt1, dt2)
        True


        >>> dt1 = {'a': {"b": {"c": [1,2,3,[4,5,6], {"d": {"e":"f"}}]}}}
        >>> dt2 = {'a': {"b": {"c": [1,2,3,[4,5,6], {"d": {"e1":"f"}}]}}}
        >>> dict_diff(dt1, dt2)
        True

        >>> dt1 = {'a': {"b": {"c": [1,2,3,[4,5,6], {"d": {"e":"f"}}]}}}
        >>> dt2 = {'a': {"b": {"c": [1,2,3,[4,5,6], {"d": {"e":"f"}}]}}}
        >>> dict_diff(dt1, dt2)
        False

        '''

        left_keys = sorted(left_dict.keys())
        right_keys = sorted(right_dict.keys())

        if left_keys == right_keys:

            keys = left_keys

            has_diff = False
            for key in keys:

                left_value = left_dict.get(key)
                right_value = right_dict.get(key)

                if type(left_value) != type(right_value):
                    has_diff = True
                    break
                else:
                    if isinstance(left_value, dict):
                        has_diff = self.dict_diff(left_value, right_value)
                        if has_diff:
                            break
                    elif isinstance(left_value, (list, tuple)):
                        has_diff = self.list_diff(left_value, right_value)
                        if has_diff:
                            break
                    else:
                        has_diff = left_value != right_value
                        if has_diff:
                            break
            return has_diff
        else:
            return True