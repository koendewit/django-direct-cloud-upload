# django-direct-cloud-upload (DDCU)
Widget for uploading files from the client directly to a cloud storage bucket. Currently only supports [Google Cloud Storage](https://cloud.google.com/storage/).

Works with Internet Explorer 11, Google Chrome, Mozilla Firefox and Apple Safari.

## Installation and setup

Install DDCU using pip :

    pip install django-direct-cloud-upload

Make sure that `'django.contrib.staticfiles'` is [set up properly](https://docs.djangoproject.com/en/stable/howto/static-files/) and add `'ddcu'` to your `INSTALLED_APPS` setting :

    INSTALLED_APPS = [
        # ...
        'django.contrib.staticfiles',
        # ...
        'ddcu',
    ]
    
    STATIC_URL = '/static/'
    
DDCU provides a view that will generate a 'signed URL' for uploading a file. To enable this view, include DDCU's `urlpatterns` to your project's URLconf :

    import ddcu
    
    urlpatterns = [
        # ...
        path('ddcu/', include(ddcu.urlpatterns)),
    ]
    
_Note_: It is not mandatory to choose `ddcu/` as the path, you are free to set any path.

## Usage

Create a `Bucket` first :

    from google.cloud import storage
    client = storage.Client()
    gcs_bucket = client.get_bucket('bucket-id-here')
    
Creating the `Client` can be a bit more complicated if you need to authenticate, see the [GCS Python client documentation](https://googleapis.dev/python/storage/latest/client.html).

Now you can use the `CloudFileWidget` for any `django.forms.CharField` in a Form :

    from ddcu import CloudFileWidget

    class EbookForm(forms.ModelForm):
        class Meta:
            model = Ebook
            fields = ['title', 'pdf_file']
            widgets = {
                'pdf_file': CloudFileWidget(
                    widget_identifier = "ebook_pdf_file",
                    bucket = gcs_bucket,
                    path_prefix = "ebook_pdf/",
                )
            }
            
`CloudFileWidget` has required parameters:

* `widget_identifier` (string): identifier for the widget, should be unique in your project. Only use uppercase and lowercase characters, numbers, underscores and hyphens.
* `bucket`: GCS `Bucket` object where the files will be uploaded.

`CloudFileWidget` has some optional parameters:

* `path_prefix` (string): Will be prepended automatically to the path of each file. This is useful for collecting all files uploaded via this widget into one directory.
* `include_timestamp` (bool) : Determines if a timestamp will be added to the path. Defaults to `True`.
* `object_identifier` (str) : Identifier (not necessarily unique) that will be added to the path.
* `timeout` (int) : Timeout (in seconds) for the signed URL. Defaults to 3600.
* `authorize_func` : Function that should raise a `ddcu.AuthenticationError` if the user is not allowed to upload a file using this widget. The function will receive three parameters: The request object, the Content Type of the file being uploaded and the object identifier (if set).
* `allow_anonymous` (bool) : Allow users that aren't logged in to upload files. Defaults to `False`.

When the form is being submitted, the field will contain the path in the bucket where the file has been uploaded to.