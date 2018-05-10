# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from apiview.model import AbstractUserMixin, BaseModel
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(AbstractUserMixin, BaseModel, AbstractBaseUser):
    is_staff = False

    def get_short_name(self):
        return self.name

    def get_full_name(self):
        return self.nickname

    USERNAME_FIELD = 'username'
    username = models.CharField('用户名', unique=True, max_length=64, editable=False, null=False, blank=False)
    password = models.CharField('密码', max_length=128, unique=True, editable=False, null=False, blank=True)
    nickname = models.CharField('昵称', unique=True, max_length=64, editable=False, null=False, blank=False)

    class Meta:
        db_table = 'example_user'
        app_label = 'example_app'
        verbose_name = verbose_name_plural = "用户"
