#! /usr/bin/env python
# encoding: utf-8
from os import environ

from django.template import Library


register = Library()

@register.inclusion_tag("apiview/scripts.html", takes_context=True)
def apiview(context):
    return context