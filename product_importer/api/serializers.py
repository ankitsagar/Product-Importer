# Django Imports
from django.core.exceptions import ValidationError

# DRF Imports
from rest_framework import serializers

# App imports
from product.tasks import import_bulk_product

# Other Imports
import os


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
        import_bulk_product(_file)

        # this function has to return something otherwise DRF will raise
        # exception
        return "success"
