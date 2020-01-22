#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from django.forms import Widget
from django.urls import reverse
from django.utils import baseconv
from django.core.signing import Signer

signer = Signer()

class CloudFileWidget(Widget):
    template_name = "cloud_file_widget.html"
    def __init__(self,
                 bucket_identifier: str,
                 path_prefix: str = "",
                 include_timestamp: bool = True,
                 submit_timeout: int = 36 * 3600,
                 clearable = True,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_identifier = bucket_identifier
        self.path_prefix = path_prefix
        self.include_timestamp = include_timestamp
        self.submit_timeout = submit_timeout
        self.clearable = clearable

    def get_context(self, name, value, attrs):
        context = super(CloudFileWidget, self).get_context(name, value, attrs)
        include_timestamp_indicator = '1' if self.include_timestamp else '0'
        valid_until = baseconv.base62.encode(int(time.time()) + self.submit_timeout)
        to_sign = f"{self.bucket_identifier}/{self.path_prefix}:{include_timestamp_indicator}:{valid_until}"
        context['ddcu_token'] = signer.sign(to_sign)
        context['guu_path'] = reverse('ddcu-get-upload-url')
        context['current_file_name'] = value.rsplit('/', 1)[-1] if value else ""
        context['input_clearable'] = self.clearable
        return context