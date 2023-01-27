from django.db import models
from django.conf import settings

from core.business.models import Business
from core.config.choices import DiscountType, ProductCategory, ProductStatus


class Discount(models.Model):
    description = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=50, blank=True)
    price = models.FloatField(default=0)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(
        max_length=12, choices=ProductStatus.choices, default=ProductStatus.AVAILABLE
    )
    favourite = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="user_favourite"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["name", "product_no"]

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    name = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductFavorite(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="favorites_count"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_products",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
