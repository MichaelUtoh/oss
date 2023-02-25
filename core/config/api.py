import hmac
import hashlib
import json

from django.conf import settings

from decouple import config

from paystackapi.paystack import Paystack
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class WebHookViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def paystack_webhook(self, request):
        secret = settings.PAYSTACK_SECRET_KEY
        paystack = Paystack(secret_key=secret)
        transaction = paystack.transaction.list()
        return Response(status=status.HTTP_200_OK)
