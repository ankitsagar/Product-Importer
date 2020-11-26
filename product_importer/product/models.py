from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=512)
    sku = models.CharField(max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product"
        ordering = ["name"]
