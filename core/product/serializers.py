from rest_framework import serializers
from core.accounts.serializers import UserDetailsSerializer
from core.business.serializers import BusinessBasicSerializer

from core.product.models import OrderItem, Product


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


class OrderItemListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "customer", "product", "quantity", "price", "created_at"]

    def get_price(self, obj):
        return obj.get_item_price()


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["quantity"]

    def save(self):
        item = OrderItem.objects.create(
            customer=self.context["customer"],
            product=self.context["product"],
            quantity=self.validated_data["quantity"],
        )
        return item

    def to_representation(self, instance):
        return OrderItemListSerializer(instance=instance, context=self.context).data
