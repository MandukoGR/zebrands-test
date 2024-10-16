from django.db import models
import uuid
from rest_framework.pagination import PageNumberPagination


class Product(models.Model):
    """
    Model for Product.
    """
    sku = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    brand = models.CharField(max_length=255, null=False, blank=False)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False)
    views = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        Overriding the save method to ensure views are never negative.
        """
        if self.views < 0:
            self.views = 0

        # If no SKU is provided, generate a new one
        if self.sku is None:
            self.sku = uuid.uuid4()

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductPagination(PageNumberPagination):
    """
    Pagination class for Product model.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
