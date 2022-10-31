from rest_framework import serializers
from core.business.serializers import BusinessBasicSerializer

from core.product.models import Product


class ProductQtySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class ProductListSerializer(serializers.ModelSerializer):
    business = BusinessBasicSerializer()

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
        ]


class ProductBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_no",
            "description",
            "category",
            "quantity",
            "unit",
            "price",
            "tax",
            "created_at",
        ]


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


class ProductUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


