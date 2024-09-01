import json
import time

from django.forms import Widget
from django.urls import reverse
from django.core.signing import Signer, b62_encode

signer = Signer()


def get_filename_from_path(path: str) -> str:
    return path.rsplit('/', 1)[-1] if path else ""


class CloudFileWidget(Widget):
    template_name = "cloud_file_widget.html"
    def __init__(self,
                 bucket_identifier: str,
                 path_prefix: str = "",
                 include_timestamp: bool = True,
                 submit_timeout: int = 36 * 3600,
                 clearable: bool = True,
                 immediate_submit: bool = False,
                 show_replace_button: bool = True,
                 allow_multiple: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_identifier = bucket_identifier
        self.path_prefix = path_prefix
        self.include_timestamp = include_timestamp
        self.submit_timeout = submit_timeout
        self.clearable = clearable
        self.immediate_submit = immediate_submit
        self.show_replace_button = show_replace_button
        self.allow_multiple = allow_multiple

    def get_context(self, name, value, attrs):
        context = super(CloudFileWidget, self).get_context(name, value, attrs)
        include_timestamp_indicator = '1' if self.include_timestamp else '0'
        allow_multiple_indicator = '1' if self.allow_multiple else '0'
        valid_until = b62_encode(int(time.time()) + self.submit_timeout)
        to_sign = f"{self.bucket_identifier}/{self.path_prefix}:{include_timestamp_indicator}:{allow_multiple_indicator}:{valid_until}"
        context['ddcu_token'] = signer.sign(to_sign)
        context['guu_path'] = reverse('ddcu-get-upload-url')
        context['input_clearable'] = self.clearable
        context['immediate_submit'] = self.immediate_submit
        context['show_replace_button'] = self.show_replace_button
        context['allow_multiple'] = self.allow_multiple
        if self.allow_multiple:
            if value:
                if value.startswith('['):
                    paths = json.loads(value)
                else:
                    paths = [value]
            else:
                paths = []
            context['existing_files'] = [(path, get_filename_from_path(path)) for path in paths]
        else:
            context['current_file_name'] = get_filename_from_path(value)
        return context
