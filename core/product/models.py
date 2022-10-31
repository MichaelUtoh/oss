from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings

from core.business.models import Business
from core.config.choices import ProductCategory


# Create your models here.
class Product(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(max_length=255)
    product_no = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=255,
        choices=ProductCategory.choices,
        default=ProductCategory.RANDOM,
    )
    image = models.ImageField(upload_to="", null=True)
    quantity = models.IntegerField(blank=True, default=1)
    unit = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["name", "product_no"]

    def calculate_total(self):
        return self.price * self.quantity

    def __str__(self) -> str:
        return self.name

