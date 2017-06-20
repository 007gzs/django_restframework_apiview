#! /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals, division

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class RequestCompatMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Kill Csrf
        if getattr(settings, "KILL_CSRF", False):
            setattr(request, '_dont_enforce_csrf_checks', True)
        # 兼容body
        ___ = request.body
        request.REQUEST = request.GET.copy()
        request.REQUEST.update(request.POST)

