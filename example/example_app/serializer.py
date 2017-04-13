#! usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

from apiview import serializer

from .models import *


class BaseSerializer(serializer.DateTimeStampSerializer):

    def __init__(self, *args, **kwargs):
        super(BaseSerializer, self).__init__(*args, **kwargs)

class UserSerializer(BaseSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'modified')