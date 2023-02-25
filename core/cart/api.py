import http.client
import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from coinbase_commerce.client import Client
from coinbase_commerce.webhook import Webhook
from decouple import config
from drf_yasg.utils import swagger_auto_schema
from paystackapi.charge import Charge
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.cart.models import Cart, CartItem, Payment
from core.cart.serializers import (
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
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CartItem.objects.filter(
            cart__user=user, pk__in=serializer.validated_data["ids"]
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=None, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=["post"])
    def checkout(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        cart = get_object_or_404(Cart, user=user)
        client = Client(api_key=config('COINBASE_COMMERCE_API_KEY'))
        charge_data = {
            'name': f'Generated charge for cart - {cart.code}',
            'description': f'Payment for {cart.code}',
            'local_price': {
                'amount': cart.total + 10,
                'currency': 'NGN'
            },
            'pricing_type': 'fixed_price',
            'metadata': {
                'order_id': cart.code
            }
        }

        try:
            charge = client.charge.create(**charge_data)
        except:
            raise serializers.ValidationError({'detail': 'Something went wrong'})

        res = {
            'id': charge.id,
            'name': charge.name,
            'amount': cart.total,
            'rates': charge.local_exchange_rates,
            'addresses': charge.addresses,
            'pricing': charge.pricing,
            'expires': charge.expires_at
        }
        return Response(data=res, status=status.HTTP_200_OK)


def handle_webhook(request):
    payload = request.body.decode('utf-8')
    signature = request.headers.get('X-CC-Webhook-Signature')
    webhook_secret = config('')

    try:
        event = Webhook.construct_event(payload, signature, webhook_secret)
    except (ValueError, Exception) as e:
        raise serializers.ValidationError({'detail': 'Something went wrong'})
    
    if event.type == 'charge:confirmed':
        # Update the order status or send a confirmation email
        pass

    return Response(status=status.HTTP_200_OK)