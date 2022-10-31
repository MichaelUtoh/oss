from django.db import transaction

import pyqrcode
from rest_framework import serializers

from core.business.models import Business, Coupon
from core.config.choices import UserType
from core.config.utils import generate_code

MAX_COUNT_OF_SHOPS_OWNED = 3


class BusinessBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "name",
            "phone",
            "address",
        ]


class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "owner",
            "name",
            "phone",
            "logo",
            "coupon_code",
            "category",
            "country",
            "address",
            "established",
            "created_at",
            "updated_at",
        ]


class BusinessCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "name",
            "phone",
            "logo",
            "coupon_code",
            "category",
            "country",
            "address",
            "established",
        ]

    def save(self):
        request = self.context["request"]
        if request.user.type not in [UserType.ADMIN, UserType.SHOP_OWNER]:
            raise serializers.ValidationError({"detail": "Not Allowed"})

        business_count = Business.objects.filter(owner=request.user).count()
        if business_count == MAX_COUNT_OF_SHOPS_OWNED:
            raise serializers.ValidationError({"detail": "You have reached maximum"})

        business = Business.objects.create(
            **self.validated_data, owner=self.context["request"].user
        )
        return business

    def update(self):
        request = self.context["request"]

        if request.user.type not in [UserType.ADMIN, UserType.SHOP_OWNER]:
            raise serializers.ValidationError({"detail": "Not Allowed"})

        business = Business.objects.filter(pk=self.context["pk"])
        if request.user != business.first().owner:
            raise serializers.ValidationError({"detail": "Not Allowed"})

        business.update(**request.data)
        return business

    def to_representation(self, instance):
        return BusinessListSerializer(instance=instance, context=self.context).data


class BusinessDeleteSerializer(serializers.Serializer):
    passcode = serializers.CharField()

    def validate_passcode(self, value):
        business = self.context["business"]
        if value.lower() != f"{business.name.lower()}":
            raise serializers.ValidationError(
                {"detail": "Enter passcode to carry out this action"}
            )
        return value


class CouponListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "business",
            "description",
            "code",
            "value",
            "qr_image",
            "active",
            "num_available",
            "num_used",
            "created_at",
        ]


class CouponCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "description",
            "value",
            "num_available",
        ]

    def save(self):
        business = self.context["business"]
        with transaction.atomic():
            code = generate_code()
            url = pyqrcode.create(code)
            image = url.png(f"{code}.png", scale=6)
            coupon = Coupon.objects.create(
                **self.validated_data,
                business_id=business.id,
                code=code,
                qr_image=image,
            )
            return coupon

    def to_representation(self, instance):
        return CouponListSerializer(instance=instance, context=self.context).data
