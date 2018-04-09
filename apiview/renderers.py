#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from rest_framework import renderers


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):

    def __init__(self, *args, **kwargs):
        super(BrowsableAPIRenderer, self).__init__(*args, **kwargs)
        self.template = 'apiview/api.html'


class JSONPRenderer(renderers.JSONRenderer):
    """
    Renderer which serializes to json,
    wrapping the json output in a callback function.
    """

    media_type = 'application/javascript'
    format = 'jsonp'
    callback_parameter = 'callback'
    default_callback = 'callback'
    charset = 'utf-8'

    @staticmethod
    def get_query_params(request):
        if hasattr(request, 'query_params'):
            params = request.query_params
        else:
            # DRF < 3.2
            params = request.QUERY_PARAMS

        return params

    def get_callback(self, renderer_context):
        """
        Determine the name of the callback to wrap around the json output.
        """
        request = renderer_context.get('request', None)
        params = request and self.get_query_params(request) or {}
        return params.get(self.callback_parameter, self.default_callback)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders into jsonp, wrapping the json output in a callback function.

        Clients may set the callback function name using a query parameter
        on the URL, for example: ?callback=exampleCallbackName
        """
        renderer_context = renderer_context or {}
        callback = self.get_callback(renderer_context)
        json = super(JSONPRenderer, self).render(data, accepted_media_type,
                                                 renderer_context)
        return callback.encode(self.charset) + b'(' + json + b');'
