#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.core.cache import cache
from django.utils.encoding import force_text


class BaseCacheItem(object):
    _prefix = None
    _expire_secs = 3600 * 24

    @classmethod
    def get_prefix(cls):
        return cls._prefix

    @classmethod
    def _getkey(cls, key):
        assert cls.get_prefix() is not None
        return 'cache:%s:%s' % (cls._prefix, force_text(key))

    @classmethod
    def add(cls, key, value, timeout=None):
        if timeout is None:
            timeout = cls._expire_secs
        return cache.add(cls._getkey(key), value, timeout)

    @classmethod
    def get(cls, key, default=None):
        return cache.get(cls._getkey(key), default)

    @classmethod
    def set(cls, key, value, timeout=None):
        if timeout is None:
            timeout = cls._expire_secs
        return cache.set(cls._getkey(key), value, timeout)

    @classmethod
    def delete(cls, key):
        return cache.delete(cls._getkey(key))

    @classmethod
    def incr(cls, key, delta=1):
        if cls.get(key) is None:
            cls.set(key, 0)
        return cache.incr(cls._getkey(key), delta)

    @classmethod
    def has_key(cls, key):
        return cache.has_key(cls._getkey(key))  # NOQA

    @classmethod
    def ttl(cls, key):
        return cache.ttl(cls._getkey(key))

    @classmethod
    def get_or_set(cls, key, func, timeout=None):
        if timeout is None:
            timeout = cls._expire_secs
        return cache.get_or_set(cls._getkey(key), func, timeout)

    @classmethod
    def persist(cls, key):
        return cache.persist(cls._getkey(key))

    @classmethod
    def expire(cls, key, timeout):
        return cache.expire(cls._getkey(key), timeout)


class AdminFuncCache(BaseCacheItem):
    _prefix = None
    _expire_secs = 3600 * 24
