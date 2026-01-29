import random, string, json, datetime, time

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import django.core.signing
try:
    from django.core.signing import b62_decode
except ImportError:
    from django.utils.baseconv import base62 as b62_obj  # For Django < 5.0
    b62_decode = b62_obj.decode
from google.cloud.storage import Blob, Bucket

from .bucket_registry import _bucket_registry


URLSAFE_CHARACTERS = string.ascii_letters + string.digits + "-._~"
signer = django.core.signing.Signer()


@require_POST
def get_upload_url(request):
    if not request.POST.get('token'):
        return HttpResponseBadRequest(f"'token' is a required parameter.")
    try:
        token: str = signer.unsign(request.POST['token'])
    except django.core.signing.BadSignature:
        return HttpResponseBadRequest("Invalid token.")

    bucket_and_path, include_timestamp_indicator, allow_multiple_indicator, exptime = token.rsplit(':', 3)
    if time.time() > b62_decode(exptime):
        return HttpResponseBadRequest("Timeout expired.")
    timestring: str = "{0:%Y-%m-%d_%H-%M-%S/}".format(timezone.now()) if include_timestamp_indicator == '1' else ""

    bucketname, path_prefix = bucket_and_path[5:].split('/', 1)
    bucket: Bucket = _bucket_registry.get('gs://' + bucketname)
    if not bucket:
        return HttpResponseBadRequest(f"Unknown bucket identifier 'gs://{bucketname}'.")

    counter = 0
    urls = []
    paths = []
    while f'filename_{counter}' in request.POST and f'content_type_{counter}' in request.POST:
        randomstring: str = "".join(random.choices(URLSAFE_CHARACTERS, k=24))
        path: str = f"{path_prefix}{timestring}{randomstring}/{request.POST[f'filename_{counter}']}"
        blob: Blob = bucket.blob(path)
        urls.append(blob.generate_signed_url(
            expiration = timezone.now() + datetime.timedelta(seconds=60),
            method = 'PUT',
            content_type = request.POST[f'content_type_{counter}'],
        ))
        paths.append(path)
        counter += 1

    if allow_multiple_indicator == '0':
        inputval = paths[0]
    elif allow_multiple_indicator == '1':
        inputval = json.dumps(paths)
    else:
        raise ValueError(f"Invalid allow_multiple_indicator '{allow_multiple_indicator}'.")

    return HttpResponse(json.dumps({
        'urls': urls,
        'inputval': inputval,
    }))