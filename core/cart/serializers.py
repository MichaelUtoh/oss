from django.contrib.auth import get_user_model
from django.db import transaction
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from core.accounts.serializers import UserDetailsSerializer
from core.cart.models import Cart, CartItem
from core.config.choices import UserType
from core.config.serializers import IdListSerializer
from core.config.utils import generate_code
from core.product.models import Product
from core.product.serializers import ProductInCartSerializer

User = get_user_model()


class CartItemBasicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name")
    product_no = serializers.CharField(source="product.product_no")
    category = serializers.CharField(source="product.category")
    description = serializers.CharField(source="product.description")
    price = serializers.FloatField(source="product.price")
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "name",
            "product_no",
            "category",
            "description",
            "quantity",
            "price",
            "total",
        ]

    def get_total(self, obj):
        return obj.product.price * obj.quantity


class CartListSerializer(serializers.Serializer):
    user = UserDetailsSerializer()
    code = serializers.CharField()
    items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_items(self, obj):
        user = obj.user
        items = CartItem.objects.filter(cart__user=user)
        data = CartItemBasicSerializer(items, many=True).data
        return data

    def get_subtotal(self, obj):
        subtotal = sum([ordx.calculate_item_price() for ordx in obj.orders.all()])
        return subtotal


class CartItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["cart", "product", "quantity", "created_at"]


class CartItemBasicCreateSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()


class CartItemCreateUpdateSerializer(serializers.Serializer):
    items = serializers.ListField(child=CartItemBasicCreateSerializer())

    @transaction.atomic
    def save(self):
        user = self.context["request"].user

        if not user.is_authenticated:
            raise serializers.ValidationError(
                {"detail": "Authentication credentials were not provided."}
            )

        if not user.type == UserType.CUSTOMER:
            raise serializers.ValidationError({"detail": "Not Allowed"})

        user = get_object_or_404(User, pk=user.id)
        cart, created = Cart.objects.get_or_create(
            user=user, defaults={"user": user, "code": generate_code()}
        )

        for ordx in self.validated_data["items"]:
            qty = ordx.pop("quantity")
            product = get_object_or_404(Product, pk=ordx["product"])
            order, created = CartItem.objects.update_or_create(
                product=product, defaults={"product": product}
            )
            order.cart = cart
            order.quantity = qty
            order.save(update_fields=["cart", "quantity"])
        return cart
