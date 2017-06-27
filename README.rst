#############################
Django REST_framework APIView
#############################
.. image:: https://travis-ci.org/007gzs/django_restframework_apiview.svg?branch=master
       :target: https://travis-ci.org/007gzs/django_restframework_apiview

***********
Screenshots
***********
.. image:: https://github.com/007gzs/django_restframework_apiview/raw/master/img/demo.jpg

****************
User in your app
****************
Install using pip::

    pip install django_restframework_apiview

Add 'apiview' to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'apiview',
    )

JSONP Renderer And debug apiview with paramslist::

    REST_FRAMEWORK = {
        ...
        'DEFAULT_RENDERER_CLASSES': [
            ...
            'apiview.renderers.JSONPRenderer',
        ],
    }
    if DEBUG:
        REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('apiview.renderers.BrowsableAPIRenderer')

Add error code to settings.py::
    
    ERROR_CODE_DEFINE = (
        ('ERR_AUTH_NOLOGIN',            10001,  'No login'),
        ('ERR_AUTH_USER_EXISTS',        10002,  'User name has exists'),
        ('ERR_AUTH_USER_NOT_EXISTS',    10003,  'User not exists'),
        ('ERR_AUTH_PASSWORD',           10005,  'Password error'),
    )

edit myapp/views.py::
    
    #! usr/bin/env python
    # encoding: utf-8
    from __future__ import unicode_literals, division

    from django.db import IntegrityError, transaction
    from django.contrib.auth import authenticate, login
    from django.contrib.auth.models import User
    from apiview.err_code import ErrCode
    from apiview.exceptions import CustomError
    from apiview.view import APIView
    from apiview.views import ViewSite
    from apiview.views import fields


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
            path = '/user'


    @site
    class Login(APIBase):

        name = '用户登陆'

        def get_context(self, request, *args, **kwargs):
            user = authenticate(username=request.params.username, password=request.params.password)
            if user is None:
                raise CustomError(ErrCode.ERR_AUTH_PASSWORD)
            login(request, user)
            return self.get_default_context(user_info={'username':request.user.username, 'email':request.user.email})

        class Meta:
            path = 'user/login'
            param_fields = (
                ('username', fields.CharField(help_text='用户名')),
                ('password', fields.CharField(help_text='密码')),
            )


    @site
    class Register(APIBase):

        name = '用户注册'

        def get_context(self, request, *args, **kwargs):
            try:
                user = User.objects.create_user(request.params.username, request.params.email, request.params.password)
            except IntegrityError:
                raise CustomError(ErrCode.ERR_AUTH_USER_EXISTS)
            return self.get_default_context()

        class Meta:
            path = 'user/register'
            param_fields = (
                ('username', fields.RegexField(help_text='用户名', regex=r'^[a-zA-Z0-9_]{3,10}$')),
                ('password', fields.CharField(help_text='密码')),
                ('email', fields.EmailField(help_text='Email')),
            )

    @site
    class Info(UserAPIBase):

        name = '用户信息'

        def get_context(self, request, *args, **kwargs):
            user_info = {'username':request.user.username, 'email':request.user.email}

            return self.get_default_context(user_info=user_info)


    @site
    class Logout(UserAPIBase):

        name = '退出登陆'

        def get_context(self, request, *args, **kwargs):
            logout(request)

            return self.get_default_context()

    urlpatterns = site.urlpatterns

add to urls.py end:

    urlpatterns.append(url(r'^test/', include("myapp.views")))

*******
Example
*******
run example::

    git clone https://github.com/007gzs/django_restframework_apiview.git
    cd django_restframework_apiview/example
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    open http://127.0.0.1:8000/example.html in browser

    
