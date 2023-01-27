from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from core.cart.models import Cart, CartItem
from core.cart.serializers import (
    CartCreateUpdateSerializer,
    CartItemCreateUpdateSerializer,
    CartItemListSerializer,
    CartListSerializer,
)
from core.config.permissions import (
    AdminOnlyPermission,
    BusinessOwnerPermission,
    CustomerPermission,
)
from core.config.schema import get_auto_schema_class_by_tags
from core.product.models import Product, ProductFavorite

User = get_user_model()


class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    swagger_schema = get_auto_schema_class_by_tags(["cart"])
    permission_classes = [CustomerPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return CartListSerializer

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: CartListSerializer}
    )
    def list(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        cart = get_object_or_404(Cart, user=user)

        if not request.user.is_authenticated:
            raise serializers.ValidationError({"detail": "Not allowed"})

        data = self.get_serializer(cart).data
        return Response(data=data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.GenericViewSet):
    queryset = CartItem.objects.all().prefetch_related("cart")
    permission_classes = [CustomerPermission]

    def get_serializer_class(self):
        return CartItemCreateUpdateSerializer

    @swagger_auto_schema(request_body=None, responses=None)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
