#! usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals, division

from rest_framework import renderers


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
        
    def __init__(self, *args, **kwargs):
        super(BrowsableAPIRenderer, self).__init__(*args, **kwargs)
        self.template = 'apiview/api.html'
    
        