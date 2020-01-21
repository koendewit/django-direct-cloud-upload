#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, string, json, datetime, time

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone, baseconv
import django.core.signing
from google.cloud.storage import Blob, Bucket

from .bucket_registry import _bucket_registry

URLSAFE_CHARACTERS = string.ascii_letters + string.digits + "-._~"
REQUIRED_PARAMS = ['token', 'filename', 'content_type']

signer = django.core.signing.Signer()

@require_POST
def get_upload_url(request):
    for p in REQUIRED_PARAMS:
        if not request.POST.get(p):
            return HttpResponseBadRequest(f"'{p}' is a required parameter.")
    try:
        token: str = signer.unsign(request.POST['token'])
    except django.core.signing.BadSignature:
        return HttpResponseBadRequest("Invalid token.")

    bucket_and_path, include_timestamp_indicator, exptime = token.rsplit(':', 2)
    if time.time() > baseconv.base62.decode(exptime):
        return HttpResponseBadRequest("Timeout expired.")

    bucketname, path_prefix = bucket_and_path[5:].split('/', 1)
    bucket: Bucket = _bucket_registry.get('gs://' + bucketname)
    if not bucket:
        return HttpResponseBadRequest(f"Unknown bucket identifier 'gs://{bucketname}'.")

    filename: str = request.POST['filename']
    content_type: str = request.POST['content_type']

    timestring: str = "{0:%Y-%m-%d_%H-%M-%S/}".format(timezone.now()) if include_timestamp_indicator == '1' else ""
    randomstring: str = "".join(random.choices(URLSAFE_CHARACTERS, k=24))
    path: str = f"{path_prefix}{timestring}{randomstring}/{filename}"
    blob: Blob = bucket.blob(path)

    return HttpResponse(json.dumps({
        'url': blob.generate_signed_url(
            expiration = timezone.now() + datetime.timedelta(seconds=60),
            method = 'PUT',
            content_type = content_type,
        ),
        'path': path,
    }))