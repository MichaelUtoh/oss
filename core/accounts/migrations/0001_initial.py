# Generated by Django 4.1.2 on 2022-10-31 18:33

import core.accounts.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("first_name", models.CharField(blank=True, max_length=30)),
                ("middle_name", models.CharField(blank=True, max_length=30)),
                ("last_name", models.CharField(blank=True, max_length=30)),
                ("phone_number1", models.CharField(blank=True, max_length=30)),
                ("phone_number2", models.CharField(blank=True, max_length=30)),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female"), ("O", "Others")],
                        default="M",
                        max_length=6,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        choices=[("Mr", "Mr"), ("Mrs", "Mrs"), ("Miss", "Miss")],
                        default="Mr",
                        max_length=4,
                    ),
                ),
                (
                    "marital_status",
                    models.CharField(
                        choices=[
                            ("single", "Single"),
                            ("married", "Married"),
                            ("divorced", "Divorced"),
                            ("widowed", "Widowed"),
                        ],
                        default="single",
                        max_length=8,
                    ),
                ),
                ("address1", models.CharField(blank=True, max_length=255)),
                ("address2", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("bronze", "Bronze"),
                            ("silver", "Silver"),
                            ("gold", "Gold"),
                            ("platinum", "Platinum"),
                        ],
                        default="none",
                        max_length=10,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("shop owner", "Shop owner"),
                            ("customer", "Customer"),
                            ("archived", "Archived"),
                            ("admin", "Admin"),
                        ],
                        default="customer",
                        max_length=10,
                    ),
                ),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[
                ("objects", core.accounts.models.UserManager()),
            ],
        ),
    ]