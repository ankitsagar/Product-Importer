# Django imports
from django.core.files.storage import default_storage


# App imports
from .models import Product
from .constants import TaskStates

# Other Imports
from celery import task
from celery.exceptions import Ignore
import traceback
import csv
import io
import logging


logger = logging.getLogger(__name__)


@task(bind=True)
def import_bulk_product(self, file_path):
    """
    Celery task to create file for each entry given in file.
    Assumes the file has header of 'name', 'sku' and 'description' with
    delimiter ','.
    """
    print("File Exists:", default_storage.exists(file_path))
    tmp_file = default_storage.open(file_path, mode='r')
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
    total_products = len(list(csv.DictReader(io_string)))
    # After couting total products move the file cursor to starting
    io_string.seek(0)

    lines = csv.DictReader(io_string)
    valid_products = 0
    invalid_products = 0

    # Contains sku as key and name and description in list as value
    # {sku: [name, description]}
    product_info_map = {}
    # Maintain all unique skus found
    skus = set()
    for line in lines:
        name = line.get('name')
        sku = line.get('sku')
        description = line.get('description', "")

        # Name and SKU are mandatory
        if not name or not sku:
            invalid_products += 1
            continue

        sku = sku.lower()
        skus.add(sku)
        product_info_map[sku] = [name, description]
        valid_products += 1

        if len(skus) == 20000:
            create_and_update_products(skus, product_info_map)
            # Reset the variables
            skus = set()
            product_info_map = {}

            self.update_state(
                state=TaskStates.PROGRESS,
                meta={
                    "done": valid_products + invalid_products,
                    "total": total_products,
                    "valid_products": valid_products,
                    "invalid_products": invalid_products
                }
            )

    # There can be leftout skus if length doesn't go to 20000 in the last
    # iteration so process it.
    if skus:
        create_and_update_products(skus, product_info_map)

    import_bulk_product.update_state(
        state=TaskStates.SUCCESS,
        meta={
            "message": "File imported successfully.",
            "total": total_products,
            "valid_products": valid_products,
            "invalid_products": invalid_products
        }
    )

    tmp_file.close()
    default_storage.delete(file_path)
    # ignore the task so no other state is recorded
    raise Ignore()


def create_and_update_products(skus, product_info_map):
    """
    Takes the skus name and compares with existing records if found then it
    goes for bulk update otherwise bulk create.

    skus: set of string
    product_info_map: dict, FORMAT: {sku: [name, description]}
    """
    products = Product.objects.filter(sku__in=skus)
    sku_found = set(products.values_list('sku', flat=True))
    skus_to_create = skus - sku_found

    products_to_update = []
    for product in products:
        name, description = product_info_map[product.sku]
        product.name = name
        product.description = description
        products_to_update.append(product)

    if products_to_update:
        Product.objects.bulk_update(
            products_to_update, ['name', 'description'], batch_size=1000
        )

    products_to_create = []
    for sku in skus_to_create:
        name, description = product_info_map[sku]
        products_to_create.append(
            Product(sku=sku, name=name, description=description)
        )
    if products_to_create:
        Product.objects.bulk_create(products_to_create, batch_size=10000)
