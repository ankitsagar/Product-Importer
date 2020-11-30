# Django Imports
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# DRF Imports
from rest_framework import serializers

# App imports
from product.tasks import import_bulk_product

# Other Imports
import os
import time
import logging


logger = logging.getLogger(__name__)


def validate_file_extension(value):
    """ Validate given file has .csv file extension. """
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class FileUploadSerializer(serializers.Serializer):
    _file = serializers.FileField(
        allow_empty_file=False, validators=[validate_file_extension]
    )

    def create(self, validated_data):
        _file = validated_data['_file']

        # Taking current timestamp as name so it'll be unique most of the time
        file_name = "tmp/" + str(time.time()) + ".csv"
        path = default_storage.save(
            file_name, ContentFile(_file.read())
        )
        logger.info("File Size: %s", default_storage.size(path))
        logger.info("File Exists: %s", default_storage.exists(path))
        # tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        task = import_bulk_product.delay(path)
        self.task_id = task.id
        logger.info("Task ID: %s, File Name: %s", task.id, file_name)
        # this function has to return something otherwise DRF will raise
        # exception
        return "success"
