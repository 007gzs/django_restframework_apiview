# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from importlib import import_module

from django.conf import settings

from .view import APIView


def get_url(head, urlpattern):
    url = getattr(urlpattern, 'pattern', urlpattern).regex.pattern
    ret = head + url.replace('\\', '').rstrip("$?").lstrip('^')
    return ret.replace('//', '/')


def get_view_list(urlpattern=None, head='/'):
    ret = []
    if urlpattern is None:
        rooturl = import_module(settings.ROOT_URLCONF)
        for urlpattern in rooturl.urlpatterns:
            ret += get_view_list(urlpattern, get_url(head, urlpattern))
        return ret
    if hasattr(urlpattern, 'callback') \
            and urlpattern.callback \
            and hasattr(urlpattern.callback, 'view_class') \
            and issubclass(urlpattern.callback.view_class, APIView):
        retdict = dict()
        viewclass = urlpattern.callback.view_class
        retdict['viewclass'] = viewclass
        retdict['params'] = viewclass._meta.param_fields
        retdict['name'] = getattr(viewclass, 'name', viewclass.__name__)
        retdict['url'] = head.replace('//', '/').rstrip('/')
        ret.append(retdict)

    if hasattr(urlpattern, 'url_patterns'):
        for pattern in urlpattern.url_patterns:
            ret += get_view_list(pattern, get_url(head, pattern))

    return ret
