#! usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals, division

import json
from apiview.err_code import ErrCode
from apiview.exceptions import CustomError
from apiview.view import APIView
from apiview.views import ViewSite
from apiview.views import fields
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate, login

from .serializer import *


site = ViewSite(name='base', app_name='base')


class APIBase(APIView):

    class Meta:
        path = '/'
        param_fields = (
            ('channel', fields.CharField(help_text='App Channel', required=False)),
            ('version', fields.CharField(help_text='App Version', required=False)),
        )


class UserAPIBase(APIBase):

    def check_user_permission(self, request):
        user = request.user
        if not user.is_authenticated() or not isinstance(user, User):
            raise CustomError(ErrCode.ERR_AUTH_NOLOGIN)

    def view(self, request, *args, **kwargs):
        self.check_user_permission(request)
        return super(APIBase, self).view(request, *args, **kwargs)

    class Meta:
        path = '/'


@site
class UserLogin(APIBase):

    name = '用户登陆'

    def get_context(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.params.username).first()
        if user is None:
            raise CustomError(ErrCode.ERR_AUTH_USER_NOT_EXISTS)
        if not user.check_password(request.params.password):
            raise CustomError(ErrCode.ERR_AUTH_PASSWORD)
        user = authenticate(example_username=request.params.username, example_password=request.params.password)
        if user is None:
            raise CustomError(ErrCode.ERR_AUTH_USER_NOT_EXISTS)
        login(request, user)
        return self.get_default_context(user_info=UserSerializer(request.user).data)

    class Meta:
        param_fields = (
            ('username', fields.CharField(help_text='用户名')),
            ('password', fields.CharField(help_text='密码')),
        )


@site
class UserRegister(APIBase):

    name = '用户注册'

    def get_context(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user = User()
                user.nickname = request.params.nickname
                user.username = request.params.username
                user.set_password(request.params.password)
                user.save()
        except IntegrityError:
            raise CustomError(ErrCode.ERR_AUTH_USER_EXISTS)
        return self.get_default_context()

    class Meta:
        param_fields = (
            ('username', fields.RegexField(help_text='用户名', regex=r'^[a-zA-Z0-9_]{3,10}$')),
            ('password', fields.CharField(help_text='密码')),
            ('nickname', fields.CharField(help_text='昵称')),
        )

@site
class UserInfo(UserAPIBase):

    name = '用户信息'

    def get_context(self, request, *args, **kwargs):
        if self.is_ws:
            data = dict()
            data["test"] = "test push"
            self.ws_reply_channel.send({"text": json.dumps(data)})
        return self.get_default_context(user_info=UserSerializer(request.user).data)


# @site
# class ParamFieldInfo(APIBase):

#     name = 'Param Field Info'

#     def get_context(self, request, *args, **kwargs):
#         return self.get_default_context(params=map(lambda x: {x:getattr(request.params, x)}, request.params._bounded_form.cleaned_data.keys()))

#     class Meta:
#         path = 'param_file_info'
#         param_fields = (
#             ('boolean_field', fields.BooleanField(help_text='Boolean Field', required=False)),
#             ('char_field', fields.CharField(help_text='Char Field', required=False)),
#             ('choice_field', fields.ChoiceField(help_text='Choice Field', required=False)),
#             ('combo_field', fields.ComboField(help_text='Combo Field', required=False)),
#             ('date_field', fields.DateField(help_text='Date Field', required=False)),
#             ('datetime_field', fields.DateTimeField(help_text='DateTime Field', required=False)),
#             ('decimal_field', fields.DecimalField(help_text='Decimal Field', required=False)),
#             ('duration_field', fields.DurationField(help_text='Duration Field', required=False)),
#             ('email_field', fields.EmailField(help_text='Email Field', required=False)),
#             ('file_field', fields.FileField(help_text='File Field', required=False)),
#             ('float_field', fields.FloatField(help_text='Float Field', required=False)),
#             ('genericipaddress_field', fields.GenericIPAddressField(help_text='GenericIPAddress Field', required=False)),
#             ('image_field', fields.ImageField(help_text='Image Field', required=False)),
#             ('integer_field', fields.IntegerField(help_text='Integer Field', required=False)),
#             ('latitude_field', fields.LatitudeField(help_text='Latitude Field', required=False)),
#             ('longitude_field', fields.LongitudeField(help_text='Longitude Field', required=False)),
#             ('mobile_field', fields.MobileField(help_text='Mobile Field', required=False)),
#             ('multiplechoice_field', fields.MultipleChoiceField(help_text='MultipleChoice Field', required=False)),
#             ('nullboolean_field', fields.NullBooleanField(help_text='NullBoolean Field', required=False)),
#             ('pairchar_field', fields.PairCharField(help_text='PairChar Field', required=False)),
#             ('regex_field', fields.RegexField(regex=r'[a-zA-Z0-9]', help_text='Regex Field', required=False)),
#             ('slug_field', fields.SlugField(help_text='Slug Field', required=False)),
#             ('splitchar_field', fields.SplitCharField(help_text='SplitChar Field', required=False)),
#             ('splitdatetime_field', fields.SplitDateTimeField(help_text='SplitDateTime Field', required=False)),
#             ('time_field', fields.TimeField(help_text='Time Field', required=False)),
#             ('timestamp_field', fields.TimestampField(help_text='Timestamp Field', required=False)),
#             ('typedchoice_field', fields.TypedChoiceField(help_text='TypedChoice Field', required=False)),
#             ('typedmultiplechoice_field', fields.TypedMultipleChoiceField(help_text='TypedMultipleChoice Field', required=False)),
#             ('url_field', fields.URLField(help_text='URL Field', required=False)),
#         )

urlpatterns = site.urlpatterns
