#! /usr/bin/env python
# encoding: utf-8
from apiview.consumers import ApiViewConsumer


channel_routing = [
    ApiViewConsumer.as_route(path="^/apiview")
]
