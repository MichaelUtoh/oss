from django.db import transaction
from django.db.models.functions import JSONObject

from rest_framework import serializers

from core.accounts.serializers import UserDetailsSerializer
from core.business.serializers import BusinessBasicSerializer
from core.config.serializers import IdListSerializer
from core.config.utils import generate_code
from core.product.models import Product, ProductFavorite, ProductImage
from core.cart.models import Cart, CartItem


class ProductImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "name", "url", "created_at"]


class ProductQtySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class ProductListSerializer(serializers.ModelSerializer):
    business = BusinessBasicSerializer()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_no",
            "description",
            "category",
            "unit",
            "price",
            "tax",
            "business",
            "images",
        ]

    def get_images(self, obj):
        return ProductImage.objects.filter(product=obj).values(
            "id", "name", "url", "created_at"
        )


class ProductBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_no",
            "description",
            "category",
            "unit",
            "price",
            "tax",
            "created_at",
        ]


class ProductInCartSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ["name", "price", "product_no", "description"]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "product_no",
            "description",
            "unit",
            "price",
            "tax",
        ]

    def to_representation(self, instance):
        return ProductListSerializer(instance=instance, context=self.context).data


class ProductFavoriteListSerializer(serializers.ModelSerializer):
    product = ProductBasicSerializer()

    class Meta:
        model = ProductFavorite
        fields = ["product"]
