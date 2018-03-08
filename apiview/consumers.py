#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from channels.generic.websockets import JsonWebsocketConsumer
from channels.handler import AsgiRequest
from django.conf import settings
from django.core import urlresolvers
from django.urls import Resolver404


class ApiViewConsumer(JsonWebsocketConsumer):
    http_user = True
    # Set to True if you want it, else leave it out
    strict_ordering = False
    CONNECT_CONTENT_KEY = 'CONNECT_CONTENT'

    def __init__(self, message, **kwargs):
        super(ApiViewConsumer, self).__init__(message, **kwargs)

    @property
    def request(self):
        if not hasattr(self, "_request"):
            msg = self.message
            connect_content = msg.channel_session.get(self.CONNECT_CONTENT_KEY, None)
            if connect_content is not None:
                msg = msg.copy()
                for k in connect_content.keys():
                    if k not in msg:
                        msg[k] = connect_content[k]
            request = AsgiRequest(msg)
            setattr(self, "_request", request)
        return getattr(self, "_request")

    @staticmethod
    def get_response(request, path, data, user, reply_channel):
        from .view import APIView
        resolver = urlresolvers.RegexURLResolver(r'^/', settings.ROOT_URLCONF)
        resolver_match = resolver.resolve(path)
        callback, callback_args, callback_kwargs = resolver_match
        if not hasattr(callback, 'view_class') or not issubclass(callback.view_class, APIView):
            raise Resolver404
        request.resolver_match = resolver_match
        response = callback(request, is_ws=True, ws_data=data, ws_user=user, 
                            ws_reply_channel=reply_channel, *callback_args, **callback_kwargs)
        return response

    def connection_groups(self, **kwargs):
        return ["apiview"]

    def connect(self, message, **kwargs):
        super(ApiViewConsumer, self).connect(message, **kwargs)
        message.channel_session[self.CONNECT_CONTENT_KEY] = message.content

    def receive(self, content, **kwargs):
        path = content.get("path", None)
        reqid = content.get("reqid", None)
        data = content.get("data", None)
        res = dict()
        try:
            response = self.get_response(self.request, path, data, getattr(self.message, "user", None), self.message.reply_channel)
            res['data'] = response.data
            res['status_code'] = response.status_code
        except Resolver404:
            res['status_code'] = 404
        except:
            res['status_code'] = 500
        res['reqid'] = reqid
        self.send(res)

    def disconnect(self, message, **kwargs):
        pass
