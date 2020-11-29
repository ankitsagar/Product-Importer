# Django imports
from django.conf import settings

# App imports
from .models import Product
from .constants import TaskStates

# Other Imports
from celery import task
from celery.exceptions import Ignore
import traceback
import csv
import io
import os


@task(bind=True)
def import_bulk_product(self, file_path):
    """
    Celery task to create file for each entry given in file.
    Assumes the file has name at first, sku at second and description as third
    index with delimiter ','.
    """
    tmp_file = open(os.path.join(settings.MEDIA_ROOT, file_path), 'r', newline="")
    try:
        decoded_file = tmp_file.read()
        io_string = io.StringIO(decoded_file)
    except UnicodeDecodeError as e:
        # Invalid file is uploaded as .csv extension

        # Added 'exc_type' and 'exc_message' in meta so while catching state of
        # task it won't throw any error on accessing meta
        self.update_state(
            state=TaskStates.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': traceback.format_exc().split('\n'),
                "message": "Invalid file provided!!"
            }
        )
        # ignore the task so no other state is recorded
        raise Ignore()
    lines = csv.reader(io_string, delimiter=',')
    total_products = len(list(lines))
    # After couting total products move the file cursor to starting and skip 1
    # line to avoid header
    io_string.seek(1)
    valid_products = 0
    invalid_products = 0
    for line in lines:
        try:
            name = line[0]
            sku = line[1]
        except IndexError:
            invalid_products += 1
            continue

        # Blank description is allowed
        try:
            description = line[2]
        except IndexError:
            description = ""

        # Name and SKU are mandatory
        if not name or not sku:
            invalid_products += 1
            continue
        Product.objects.update_or_create(
            sku__iexact=sku,
            defaults={
                'name': name,
                'description': description,
                'sku': sku
            }
        )
        valid_products += 1
        self.update_state(
            state=TaskStates.PROGRESS,
            meta={
                "done": valid_products + invalid_products,
                "total": total_products,
                "valid_products": valid_products,
                "invalid_products": invalid_products
            }
        )
    import_bulk_product.update_state(
        state=TaskStates.SUCCESS,
        meta={
            "message": "File imported successfully.",
            "total": total_products,
            "valid_products": valid_products,
            "invalid_products": invalid_products
        }
    )
    # ignore the task so no other state is recorded
    raise Ignore()
