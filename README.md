# django-direct-cloud-upload (DDCU)
Widget for uploading files from the client directly to a cloud storage bucket. Currently only supports [Google Cloud Storage](https://cloud.google.com/storage/).

Works with Internet Explorer 11, Google Chrome, Mozilla Firefox and Apple Safari.

## Installation and setup

Install DDCU using pip :

    pip install django-direct-cloud-upload

Make sure that `'django.contrib.staticfiles'` is [set up properly](https://docs.djangoproject.com/en/stable/howto/static-files/) and add `'direct_cloud_upload'` to your `INSTALLED_APPS` setting :

    INSTALLED_APPS = [
        # ...
        'django.contrib.staticfiles',
        # ...
        'direct_cloud_upload',
    ]
    
    STATIC_URL = '/static/'
    
DDCU provides a view that will generate a 'signed URL' for uploading a file. To enable this view, include DDCU's `urlpatterns` to your project's URLconf :

    import direct_cloud_upload
    
    urlpatterns = [
        # ...
        path('direct_cloud_upload/', include(direct_cloud_upload.urlpatterns)),
    ]
    
_Note_: It is not mandatory to choose `direct_cloud_upload/` as the path, you are free to set any path.

## Configuring the GCS bucket

If you don't have a GCS bucket yet, [create one](https://cloud.google.com/storage/docs/creating-buckets) first.

[Configure CORS](https://cloud.google.com/storage/docs/configuring-cors) on your bucket to allow uploads from your website. Configuring CORS for GCS buckets is done by creating a JSON-file describing the CORS policy and uploading the JSON file with `gsutil`.

Example JSON file containing a CORS policy:

    [
        {
            "origin": [
                "https://example-app.com",
                "https://www.example-app.com",
                "http://localhost:8000"
            ],
            "responseHeader": ["Content-Type"],
            "method": ["GET", "HEAD", "PUT"],
            "maxAgeSeconds": 3600
        }
    ]
    
Upload the JSON file with the `gsutil cors set` command:

    gsutil cors set cors-json-file.json gs://example-bucket

## Usage

Create a `Bucket` instance and register it with DDCU :

    import google.cloud.storage
    import direct_cloud_upload
    
    client = google.cloud.storage.Client()
    gcs_bucket = client.get_bucket('bucket-id-here')
    ddcu_bucket_identifier = direct_cloud_upload.register_gcs_bucket(gcs_bucket)
    
Creating the `Client` can be a bit more complicated if you need to authenticate, see the [GCS Python client documentation](https://googleapis.dev/python/storage/latest/client.html).

Now you can use the `CloudFileWidget` for any `django.forms.CharField` in a Form :

    from direct_cloud_upload import CloudFileWidget

    class EbookForm(forms.ModelForm):
        class Meta:
            model = Ebook
            fields = ['title', 'pdf_file']
            widgets = {
                'pdf_file': CloudFileWidget(
                    bucket_identifier = ddcu_bucket_identifier,
                    path_prefix = "ebook_pdf/",
                )
            }
            
`CloudFileWidget` has one required parameter:

* `bucket_identifier` (string): identifier retrieved when registering the bucket with DDCU.

`CloudFileWidget` has some optional parameters:

* `path_prefix` (string): Will be prepended automatically to the path of each file. This is useful for collecting all files uploaded via this widget into one directory.
* `include_timestamp` (bool) : Determines if a timestamp will be added to the path. Defaults to `True`.
* `submit_timeout` (int) : Timeout (in seconds) for uploading the form. Defaults to 129600 (36 hours).
* `clearable` (bool) : Add a "Delete file" button to the widget. Defaults to `True`.

When the form is being submitted, the field will contain the path in the bucket where the file has been uploaded to.

## Including static JS and CSS files

DDCU needs a Javascript and CSS file to function. If you use the widget in a django-admin site, you can use the first method to include these files. For all other sites, you should read the "For generic forms" section below.

### For admin sites

Add a `Meta` model to your Admin classes:

    class EbookAdmin(admin.ModelAdmin):
        form = EbookForm
        class Media:
            css = { 'all': ("direct_cloud_upload/cloud_file_widget.css", ) }
            js = ("direct_cloud_upload/ddcu_upload.js", )

### For generic forms

Every page containing a `CloudFileWidget` should include jQuery 1.9 (or newer) and the JS and CSS file in the `head` section:

    {% load static %}
    
    <head>
        <link rel="stylesheet" href="{% static "direct_cloud_upload/cloud_file_widget.css" %}"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
        <script src="{% static "direct_cloud_upload/ddcu_upload.js" %}"></script>
    </head>