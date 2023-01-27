from django.conf import settings

from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.accounts.models import User
from core.accounts.serializers import (
    UserBasicSerializer,
    UserDetailsSerializer,
    UserDetailsTokenSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
)
from core.config.choices import UserType
from core.config.permissions import AdminOnlyPermission, BusinessOwnerPermission
from core.config.services import filter_http_method_names


class UserDetailViewSet(
    mixins.UpdateModelMixin,
    # mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    http_method_names = filter_http_method_names(["patch"])

    def get_serializer_class(self):
        if self.action == "update":
            return UserBasicSerializer
        if self.action in ["details", "list", "retrieve"]:
            return UserDetailsSerializer

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: UserDetailsSerializer}
    )
    @action(detail=False, methods=["get"])
    def details(self, request, *args, **kwargs):
        data = self.get_serializer(request.user).data
        return Response(data=data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"pk": self.kwargs["pk"], "request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.update()
        return Response(data=serializer.data)


class UserTokenResponseMixin:
    def get_user_token_response_data(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        access_token.set_exp(lifetime=timedelta(seconds=settings.WEB_TOKEN_EXPIRY))
        data = {
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
            "user": user,
        }

        return UserDetailsTokenSerializer(data, context={"request": self.request}).data


class UserRegisterAPIView(UserTokenResponseMixin, GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserRegisterSerializer,
        responses={status.HTTP_201_CREATED: UserDetailsSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.get_user_token_response_data(user)
        return Response(data=data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(UserTokenResponseMixin, GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserLoginSerializer, responses={200: UserDetailsTokenSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = self.get_user_token_response_data(user)
        return Response(data)


class UserDetailUpdateView(GenericAPIView):
    serializer_class = UserBasicSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserLoginSerializer, responses={200: UserDetailsSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(user)
