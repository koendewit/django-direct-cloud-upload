#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path

from .widgets import CloudFileWidget
from .views import get_upload_url
from .bucket_registry import register_gcs_bucket

urlpatterns = [path("get_upload_url", get_upload_url, name='ddcu-get-upload-url')]

__all__ = [
    'CloudFileWidget', 'urlpatterns', 'register_gcs_bucket',
]

default_app_config = "direct_cloud_upload.apps.DdcuConfig"