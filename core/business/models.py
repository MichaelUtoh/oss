from uuid import uuid4

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

from django_countries.fields import CountryField
from imagekit.models.fields import ProcessedImageField
from pilkit.processors.resize import ResizeToFit

from core.config.choices import BusinessRating


# Create your models here.
class Business(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="businesses"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    logo = ProcessedImageField(
        upload_to="static/businesses/",
        blank=True,
        processors=[ResizeToFit(300, 300)],
        format="PNG",
        options={"quality": 90},
    )
    coupon_code = models.CharField(max_length=64, blank=True)
    category = models.CharField(max_length=128, blank=True)
    country = CountryField(blank=True)
    address = models.CharField(max_length=255)
    established = models.DateField(blank=True)
    rating = models.CharField(
        max_length=7,
        choices=BusinessRating.choices,
        default=BusinessRating.LEVEL_1,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_owner(self, user):
        return self.owner == user


class BusinessFavorite(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="favorites_count"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_shops",
    )


class Coupon(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.PROTECT, related_name="generated_coupons"
    )
    code = models.CharField(max_length=50)
    description = models.CharField(max_length=255, unique=True)
    value = models.IntegerField()
    qr_image = models.ImageField(upload_to="qr_code_store", null=True, blank=True)
    active = models.BooleanField(default=True)
    num_available = models.IntegerField(default=5)
    num_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coupon {self.code} - {self.description}"
