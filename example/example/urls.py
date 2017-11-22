#! /usr/bin/env python
# encoding: utf-8
"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import static
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from apiview.common_view import generate_api_js

urlpatterns = [
    url(r'^example.html$', TemplateView.as_view(template_name='example.html')),
    url(r'^modeladmin/', admin.site.urls),
    url(r'^example/', include("example_app.views")),
]
if settings.DEBUG:
    urlpatterns.append(
        url(r'^api.js$', generate_api_js)
    )
urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
