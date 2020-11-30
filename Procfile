web: gunicorn product_importer.wsgi
worker: celery -A product_importer worker -l info
