# Generated by Django 4.1.2 on 2022-11-21 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0003_alter_orderitem_unique_together_productfavorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
