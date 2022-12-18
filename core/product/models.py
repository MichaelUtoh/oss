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
    # image = models.ImageField(upload_to="", null=True)
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


class OrderItem(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="in_cart"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="in_cart"
    )
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["customer", "product"]

    def __str__(self) -> str:
        return f"{self.product} - {self.quantity}"

    def get_item_price(self):
        return self.product.price * self.quantity


class Cart(models.Model):
    items = models.ManyToManyField(OrderItem)
    code = models.CharField(max_length=15)
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.code
