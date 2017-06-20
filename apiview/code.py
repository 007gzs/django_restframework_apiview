#! /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals, division


class CodeData(object):

    def __init__(self, code, tag, message):
        self.code = code
        self.message = message
        self.tag = tag

    def get_res_dict(self, **kwargs):
        ret = dict(kwargs)
        ret['code'] = self.code
        if 'message' not in ret:
            ret['message'] = self.message
        return ret


class Code(object):

    def __init__(self, code_define):
        codes = set()
        self._list = list()
        self._dict = dict()
        self._tags = list()
        for tag, code, message in code_define:
            assert code not in codes and not hasattr(self, tag)
            setattr(self, tag, CodeData(code, tag, message))
            codes.add(code)
            self._tags.append(tag)
            self._list.append((code, message))
            self._dict[code] = message

    def get_list(self):
        return self._list

    def get_dict(self):
        return self._dict

    def get_tags(self):
        return self._tags