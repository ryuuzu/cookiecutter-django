from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    default_acl = "public-read"
    custom_domain = False  # Disable custom domain to force path-style URLs


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION
    file_overwrite = False
    custom_domain = False  # Disable custom domain to force path-style URLs
