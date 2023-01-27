from django.conf import settings

from django.db import models

from core.product.models import Product
from core.config.choices import CartStatus


class Payment(models.Model):
    cart = models.OneToOneField(
        "Cart", on_delete=models.CASCADE, related_name="cart_payment"
    )
    amount = models.IntegerField()
    provider = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    code = models.CharField(max_length=15)
    total = models.IntegerField(default=0)
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="cart_detail_detail", null=True
    )
    status = models.CharField(max_length=10, choices=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.code


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="products_in_cart"
    )
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.product} - {self.quantity}"

    def calculate_item_price(self):
        return self.product.price * self.quantity
