# Generated by Django 4.1.2 on 2022-10-31 18:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import imagekit.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Business",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=30)),
                (
                    "logo",
                    imagekit.models.fields.ProcessedImageField(
                        blank=True, upload_to="static/businesses/"
                    ),
                ),
                ("coupon_code", models.CharField(blank=True, max_length=64)),
                ("category", models.CharField(blank=True, max_length=128)),
                (
                    "country",
                    django_countries.fields.CountryField(blank=True, max_length=2),
                ),
                ("address", models.CharField(max_length=255)),
                ("established", models.DateField(blank=True)),
                (
                    "rating",
                    models.CharField(
                        choices=[
                            ("level 1", "Level 1"),
                            ("level 2", "Level 2"),
                            ("level 3", "Level 3"),
                            ("level 4", "Level 4"),
                            ("level 5", "Level 5"),
                        ],
                        default="level 1",
                        max_length=7,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="businesses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Coupon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=255, unique=True)),
                ("value", models.IntegerField()),
                (
                    "qr_image",
                    models.ImageField(blank=True, null=True, upload_to="qr_code_store"),
                ),
                ("active", models.BooleanField(default=True)),
                ("num_available", models.IntegerField(default=5)),
                ("num_used", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="generated_coupons",
                        to="business.business",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BusinessFavorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites_count",
                        to="business.business",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_shops",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
