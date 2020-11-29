from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_importer.settings")
app = Celery(
    "product_importer",
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
