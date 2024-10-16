from django.db import models
import uuid


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

        # If not sku is provided, generate a new one
        if self.sku is None:
            self.sku = uuid.uuid4()

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
