#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from importlib import import_module

from django.conf import settings
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response

from .view import APIView
from .err_code import ErrCode


@api_view(["GET"])
@renderer_classes((StaticHTMLRenderer,))
def generate_api_js(request):
    # api.js?package_name=bbapi.views&ext_params=referral_code,version,device_id,channel
    tags = ErrCode.get_tags()
    content = ''
    content += "server:'%s', //服务地址\n" % request.build_absolute_uri("/")[:-1]
    for tag in tags:
        code_data = getattr(ErrCode, tag)
        content += '%s:%d, //%s\n' % (tag, code_data.code, code_data.message)
    ext_params_str = request.GET.get("ext_params", '')
    ext_params = set(ext_params_str.split(','))
    views = get_view_list()
    for view in views:
        func_name = view['url'].replace('/', '_').strip('_')
        str_args = ''
        str_data = ''
        for param in view['params'].keys():
            if param in ext_params:
                continue
            str_args += ', %s' % param
            str_data += "%s:%s," % (param, param)
        
        str_data = str_data[:-1]
        content += '''
// %s
%s: function(listener%s){
    var url = '%s';
    var data = {%s};
    this.conn(url, data, listener);
},''' % (view['name'], func_name, str_args, view['url'], str_data)
    return Response(content.encode("utf8"), content_type='text/plain;charset=utf-8')


def get_url(head, urlpattern):
    url = urlpattern.regex.pattern
    ret = head + url.rstrip("$?").lstrip('^')
    return ret.replace('//', '/')


# def get_package_list(urlpattern, ext_params, head):
#     ret = ''
#     if hasattr(urlpattern, 'callback') \
#         and urlpattern.callback \
#         and hasattr(urlpattern.callback, 'view_class') \
#         and issubclass(urlpattern.callback.view_class, APIView):
#         viewclass = urlpattern.callback.view_class
#         params = viewclass._meta.param_fields
#         name = viewclass.__name__
#         # url = viewclass._meta.path[:-1]
#         url = head.replace('//', '/').rstrip('/')
#         func_name = url.replace('/', '_').strip('_')
#         str_args = ''
#         str_data = ''
#         for param in params.keys():
#             if param in ext_params:
#                 continue
#             str_args += ', %s' % param
#             str_data += "%s:%s," % (param, param)
#         ret += '''
#             // %s
#             %s: function(listener%s){
#                 var url = api.server + '%s';
#                 var data = {%s};
#                 api.conn(url, data, listener);
#             },''' % (name, func_name, str_args, url, str_data)

#     if hasattr(urlpattern, 'url_patterns'):
#         for pattern in urlpattern.url_patterns:
#             ret += get_package_list(pattern, ext_params, get_url(head, pattern))

#     return ret

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
        # func_name = url.replace('/', '_').strip('_')
        # str_args = ''
        # str_data = ''
        # for param in params.keys():
        #     if param in ext_params:
        #         continue
        #     str_args += ', %s' % param
        #     str_data += "%s:%s," % (param, param)
        # ret += '''
        #     // %s
        #     %s: function(listener%s){
        #         var url = api.server + '%s';
        #         var data = {%s};
        #         api.conn(url, data, listener);
        #     },''' % (name, func_name, str_args, url, str_data)

    if hasattr(urlpattern, 'url_patterns'):
        for pattern in urlpattern.url_patterns:
            ret += get_view_list(pattern, get_url(head, pattern))

    return ret

