from django.contrib.admin import ModelAdmin

class DdcuAdminMixin(ModelAdmin):
    class Media:
        css = {'all': ("direct_cloud_upload/cloud_file_widget.css", )}
        js = ("direct_cloud_upload/ddcu_upload.js", )
