# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging

from django.http import HttpResponse
from django.conf import settings
from django.utils.encoding import force_text
from rest_framework.response import Response

from . import utility
from .views.rest_framework import View as ViewBase
from .err_code import ErrCode
from .exceptions import CustomError
from .logger import CALLER_KEY


class APIView(ViewBase):
    ERROR_CODE_STATUS_CODE = 400
    logger = logging.getLogger('apiview')

    def get_view_name(self):
        if hasattr(self, 'name'):
            return self.name
        return super(APIView, self).get_view_name()

    def format_res_data(self, context):
        if not isinstance(context, dict) or 'code' not in context:
            context = self.get_default_context(data=context)
        status_code = 200
        if context['code'] != ErrCode.SUCCESS.code:
            status_code = self.ERROR_CODE_STATUS_CODE

        return Response(utility.format_res_data(context), status=status_code)

    def check_api_permissions(self, request, *args, **kwargs):
        pass

    def view(self, request, *args, **kwargs):
        self.logger.info("m=%s g=%s p=%s u=%s",
                         request.META, request.query_params, getattr(request, 'body', None), request.user,
                         extra={CALLER_KEY: self.get_context})
        self.check_api_permissions(request, *args, **kwargs)
        context = self.get_context(request, *args, **kwargs)
        if isinstance(context, HttpResponse):
            response = context
        else:
            response = self.format_res_data(context)
        return response

    def get(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)

    post = ws = get

    @staticmethod
    def get_default_context(**kwargs):
        return ErrCode.SUCCESS.get_res_dict(**kwargs)

    @staticmethod
    def set_code(context, code, message=None):
        context['code'] = code.code
        if message is None:
            context['message'] = code.message
        else:
            context['message'] = message

    @staticmethod
    def set_message(context, message):
        context['message'] = message

    def get_context(self, request, *args, **kwargs):
        raise NotImplementedError

    def handle_param_errors(self, exc):
        request = self.request
        self.logger.info("m=%s g=%s p=%s u=%s",
                         request.META, request.query_params, request.data, request.user,
                         extra={CALLER_KEY: self.get_context})
        context = self.get_default_context()
        self.set_code(context, ErrCode.ERR_COMMON_BAD_PARAM)
        if getattr(settings, 'APIVIEW_SHOWPARAM_INFO', settings.DEBUG):
            if hasattr(exc, 'error_dict_obj'):
                context['errors'] = exc.error_dict_obj
                context['desc'] = exc.error_dict_obj.as_text()
            else:
                context['desc'] = force_text(exc)
        return self.format_res_data(context)

    def handle_exception(self, exc):
        if isinstance(exc, CustomError):
            return self.format_res_data(exc.get_res_dict())

        if settings.DEBUG:
            raise exc

        utility.reportExceptionByMail("500")
        return self.format_res_data(ErrCode.ERR_SYS_ERROR.get_res_dict())
