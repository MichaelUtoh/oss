import pandas as pd
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.accounts.models import User
from core.business.models import Business, BusinessFavorite, Coupon
from core.business.serializers import (
    BusinessCreateUpdateSerializer,
    BusinessDeleteSerializer,
    BusinessListSerializer,
    CouponCreateUpdateSerializer,
    CouponListSerializer,
)
from core.config.permissions import AdminOnlyPermission, BusinessOwnerPermission
from core.config.schema import get_auto_schema_class_by_tags
from core.config.choices import UserType


class BusinessViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Business.objects.all().order_by("name")
    permission_classes = [AdminOnlyPermission | BusinessOwnerPermission]

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return BusinessListSerializer
        if self.action == "create" or self.action == "update":
            return BusinessCreateUpdateSerializer
        if self.action == "delete_business":
            return BusinessDeleteSerializer

    @swagger_auto_schema(
        request_body=BusinessCreateUpdateSerializer,
        responses={status.HTTP_201_CREATED: BusinessListSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        business = serializer.save()
        data = BusinessListSerializer(business).data
        return Response(data=data)

    @swagger_auto_schema(
        request_body=BusinessCreateUpdateSerializer,
        responses={status.HTTP_201_CREATED: BusinessListSerializer},
    )
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request, "pk": self.kwargs["pk"]}
        )
        serializer.is_valid(raise_exception=True)
        business = serializer.update()
        data = BusinessListSerializer(business, many=True).data
        return Response(data=data)

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: BusinessListSerializer}
    )
    # @action(detail=False, methods=["GET"])
    def list(self, request, *args, **kwargs):
        if request.user.type == UserType.CUSTOMER:
            raise serializers.ValidationError({"detail": "Not authorized"})

        business_qs = self.get_queryset()
        businesses = pd.DataFrame(business_qs.values())
        print(businesses)

        if request.user.type == UserType.SHOP_OWNER:
            business_qs = business_qs.filter(owner=self.request.user)

        data = self.get_serializer(business_qs, many=True).data
        return Response(data=data)

    @swagger_auto_schema(request_body=None, responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["POST"])
    def add_business_to_favorites(self, request, *args, **kwargs):
        if request.user.type != UserType.CUSTOMER:
            raise serializers.ValidationError({"detail": "Action not allowed"})

        if BusinessFavorite.objects.filter(
            business=self.get_object(), user=request.user
        ).exists():
            raise serializers.ValidationError(
                {"detail": "This shop is already in your favorites list"}
            )

        BusinessFavorite.objects.create(business=self.get_object(), user=request.user)
        return Response()

    @swagger_auto_schema(request_body=None, responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["POST"])
    def remove_business_from_favorites(self, request, *args, **kwargs):
        if request.user == self.get_object().owner:
            raise serializers.ValidationError({"detail": "Action not allowed"})

        if request.user.type != UserType.CUSTOMER:
            raise serializers.ValidationError({"detail": "Action not allowed"})

        BusinessFavorite.objects.filter(
            business=self.get_object(), user=request.user
        ).delete()
        return Response()

    @swagger_auto_schema(
        request_body=BusinessDeleteSerializer,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["delete"])
    def delete_business(self, request, *args, **kwargs):
        business = get_object_or_404(Business, pk=self.kwargs["pk"])
        serializer = self.get_serializer(
            data=request.data, context={"business": business}
        )
        serializer.is_valid(raise_exception=True)
        passcode = serializer.validated_data["passcode"]
        business.delete() if passcode else None
        return Response()


class CouponViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Coupon.objects.all().order_by("-created_at")
    swagger_schema = get_auto_schema_class_by_tags(["coupons"])
    permission_classes = [BusinessOwnerPermission]

    def get_serializer_class(self):
        if self.action == "create":
            return CouponCreateUpdateSerializer
        if self.action == "list":
            return CouponListSerializer

    @swagger_auto_schema(
        request_body=CouponCreateUpdateSerializer,
        responses={status.HTTP_201_CREATED: CouponListSerializer},
    )
    def create(self, request, *args, **kwargs):
        business = get_object_or_404(Business, pk=self.kwargs["business_pk"])

        if not request.user == business.owner:
            raise serializers.ValidationError({"detail": "Business not found"})

        serializer = self.get_serializer(
            data=request.data, context={"business": business}
        )

        serializer.is_valid(raise_exception=True)
        coupon = serializer.save()
        data = CouponListSerializer(coupon).data
        return Response(data=data)
