#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path

from .widgets import CloudFileWidget
from .views import get_upload_url, AuthenticationError

urlpatterns = [path("get_upload_url", get_upload_url, name='ddcu-get-upload-url')]

__all__ = [
    'CloudFileWidget', 'get_upload_url', 'AuthenticationError', 'urlpatterns',
]

default_app_config = "ddcu.apps.DdcuConfig"