#! /usr/bin/env python
# encoding: utf-8
import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
channel_layer = channels.asgi.get_channel_layer()