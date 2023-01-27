from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.cart.models import Cart, CartItem
from core.cart.serializers import (
    CartItemCreateUpdateSerializer,
    CartListSerializer,
)
from core.config.permissions import (
    CustomerPermission,
)
from core.config.schema import get_auto_schema_class_by_tags
from core.config.serializers import IdListSerializer

User = get_user_model()


class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    swagger_schema = get_auto_schema_class_by_tags(["cart"])
    permission_classes = [CustomerPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return CartListSerializer
        if self.action == "delete_order":
            return IdListSerializer

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

    @swagger_auto_schema(
        request_body=IdListSerializer, responses={status.HTTP_204_NO_CONTENT: None}
    )
    @action(detail=False, methods=["patch"])
    def delete_order(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CartItem.objects.filter(pk__in=serializer.validated_data["ids"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

