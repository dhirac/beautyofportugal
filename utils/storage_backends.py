from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings

class GoogleCloudMediaStorage(GoogleCloudStorage):
    bucket_name = settings.GS_BUCKET_NAME
    location = settings.GS_LOCATION
    credentials = settings.GS_CREDENTIALS