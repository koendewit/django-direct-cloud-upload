#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, string, json, datetime

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from google.cloud.storage import Blob

from .widgets import CloudFileWidget

URLSAFE_CHARACTERS = string.ascii_letters + string.digits + "-._~"
REQUIRED_PARAMS = ['wid', 'filename', 'content_type']

class AuthenticationError(Exception):
    def __init__(self, msg):
        self.msg = msg

@require_POST
def get_upload_url(request):
    for p in REQUIRED_PARAMS:
        if not request.POST.get(p):
            return HttpResponseBadRequest(f"'{p}' is a required parameter.")
    field = CloudFileWidget._widgetregistry.get(request.POST['wid'])
    if not field:
        return HttpResponseBadRequest(f"Unknown identifier '{request.POST['wid']}'.")

    object_identifier: str = request.POST.get('oid') # Can be None
    filename: str = request.POST['filename']
    content_type: str = request.POST['content_type']

    if not field.allow_anonymous:
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required.")

    if field.authorize_func:
        try:
            field.authorize_func(request, content_type, object_identifier)
        except AuthenticationError as ae:
            return HttpResponseForbidden(ae.msg)

    timestring: str = "{0:%Y-%m-%d_%H-%M-%S/}".format(timezone.now()) if field.include_timestamp else ""
    randomstring: str = "".join(random.choices(URLSAFE_CHARACTERS, k=24))
    if object_identifier:
        path: str = f"{field.path_prefix}{object_identifier}/{timestring}{randomstring}/{filename}"
    else:
        path: str = f"{field.path_prefix}{timestring}{randomstring}/{filename}"

    blob: Blob = field.bucket.blob(path)

    return HttpResponse(json.dumps({
        'url': blob.generate_signed_url(
            expiration=datetime.datetime.now() + datetime.timedelta(seconds=field.timeout),
            method='PUT',
            content_type=content_type,
        ),
        'path': path,
    }))