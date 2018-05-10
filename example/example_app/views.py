# encoding: utf-8
from __future__ import absolute_import, unicode_literals

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


@site
class ParamFieldInfo(APIBase):

    name = 'Param Field Info'

    def get_context(self, request, *args, **kwargs):
        return self.get_default_context(params=map(lambda x: {x:getattr(request.params, x)}, request.params._bounded_form.cleaned_data.keys()))

    class Meta:
        path = 'param_file_info'
        param_fields = (
            ('boolean_field', fields.BooleanField(help_text='help_text for this Boolean Field', required=True)),
            ('nullboolean_field', fields.NullBooleanField(help_text='help_text for this NullBoolean Field', default=None, required=False)),
            ('char_field', fields.CharField(help_text='help_text for this Char Field', max_length=64, min_length=12, default='null', required=True)),
            ('email_field', fields.EmailField(help_text='help_text for this Email Field', required=False)),
            ('mobile_field', fields.MobileField(help_text='help_text for this Mobile Field', required=False)),
            ('url_field', fields.URLField(help_text='help_text for this URL Field', required=False)),
            ('ip_field', fields.GenericIPAddressField(help_text='help_text for this GenericIPAddress Field', required=True, omit='0.0.0.0')),
            ('regex_field', fields.RegexField(regex=r'^[a-zA-Z0-9]*$', help_text='help_text for this Regex Field', required=False)),
            ('integer_field', fields.IntegerField(help_text='help_text for this Integer Field', max_value=100, min_value=0, required=False)),
            ('float_field', fields.FloatField(help_text='help_text for this Float Field', max_value=360.0, min_value=0.0, required=False)),
            ('latitude_field', fields.LatitudeField(help_text='help_text for this Latitude Field', required=False)),
            ('longitude_field', fields.LongitudeField(help_text='help_text for this Longitude Field', required=False)),
            ('decimal_field', fields.DecimalField(help_text='help_text for this Decimal Field', max_digits=10, decimal_places=2, required=False)),
            ('date_field', fields.DateField(help_text='help_text for this Date Field', required=False)),
            ('datetime_field', fields.DateTimeField(help_text='help_text for this DateTime Field', required=False)),
            ('time_field', fields.TimeField(help_text='help_text for this Time Field', required=False)),
            ('timestamp_field', fields.TimestampField(help_text='help_text for this Timestamp Field', required=False)),
            ('file_field', fields.FileField(help_text='help_text for this File Field', required=False)),
            ('image_field', fields.ImageField(help_text='help_text for this Image Field', required=False)),
            ('choice_field', fields.ChoiceField(help_text='help_text for this Choice Field', choices=((0, 100), (1, "test")), required=False)),
            ('splitchar_field', fields.SplitCharField(help_text='help_text for this SplitChar Field', sep=",", field=fields.IntegerField(), required=False)),
            ('pairchar_field', fields.PairCharField(help_text='help_text for this PairChar Field', seps=('|', '.'), fields=(fields.IntegerField(), fields.CharField()), required=False)),
        )

urlpatterns = site.urlpatterns
