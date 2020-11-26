# App imports
from .models import Product

# Other Imports
import csv
import io


def import_bulk_product(products_file):
    """
    Celery task to create file for each entry given in file.
    Assumes the file has name at first, sku at second and description as third
    index with delimiter ','.
    """
    try:
        decoded_file = products_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
    except UnicodeDecodeError:
        # Invalid file is uploaded as .csv extension
        return

    valid_products = 0
    invalid_products = 0
    for line in csv.reader(io_string, delimiter=',', quotechar='|'):
        # it's the header of file, no need to import
        if not valid_products and not invalid_products:
            continue

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

        Product.object.update_or_create(
            sku=sku,
            defaults={'name': name, 'description': description}
        )
        valid_products += 1
