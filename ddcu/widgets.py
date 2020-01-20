#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import string
from typing import Dict, Callable

from django.forms import Widget
from django.http import HttpRequest
from django.urls import reverse
from google.cloud.storage import Bucket

WIDGET_IDENTIFIER_ALLOWED_CHARACTERS = string.ascii_letters + string.digits + "-_"

class CloudFileWidget(Widget):
    _widgetregistry: Dict[str, CloudFileWidget] = dict()
    template_name = "cloud_file_widget.html"
    def __init__(self,
                 widget_identifier: str,
                 bucket: Bucket,
                 path_prefix: str = "",
                 include_timestamp: bool = True,
                 object_identifier: str = "",
                 timeout: int = 3600,
                 authorize_func: Callable[[HttpRequest, str, str], None] = None,  # Function will receive three parameters: The request object, the Content Type and the identifier.
                 allow_anonymous: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        for c in widget_identifier:
            if not c in WIDGET_IDENTIFIER_ALLOWED_CHARACTERS:
                raise ValueError("Only use ASCII letters, digits, underscores and hyphens in the widget identifier.")
        self.widget_identifier = widget_identifier
        self.bucket = bucket
        self.path_prefix = path_prefix
        self.include_timestamp = include_timestamp
        self.object_identifier = object_identifier
        self.timeout = timeout
        self.authorize_func = authorize_func
        self.allow_anonymous = allow_anonymous
        self._widgetregistry[widget_identifier] = self

    def get_context(self, name, value, attrs):
        context = super(CloudFileWidget, self).get_context(name, value, attrs)
        context['widget_identifier'] = self.widget_identifier
        context['object_identifier'] = self.object_identifier
        context['guu_path'] = reverse('ddcu-get-upload-url')
        context['current_file_name'] = value.rsplit('/', 1)[-1] if value else ""
        return context