from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from core.marketing.serializers import EmailSerializer


class EmailViewSet(viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action == "subscribe" or self.action == "unsubscribe":
            return EmailSerializer

    @swagger_auto_schema(request_body=None, responses=None)
    def subscribe(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=None, responses=None)
    def unsubscribe(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)
