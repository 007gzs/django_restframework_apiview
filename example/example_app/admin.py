# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from apiview import admin

from . import models


admin.site_register(models.User)
