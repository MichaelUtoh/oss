from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers
from rest_framework.validators import ValidationError

from core.config.choices import UserType


User = get_user_model()

INVALID_CREDENTIALS_MSG = "Unable to login with the provided credentials."


def validate_user_password_attribute_similarity(password, user):
    if settings.DEBUG:
        return

    try:
        validator = password_validation.UserAttributeSimilarityValidator()
        validator.validate(password, user)
    except ValidationError as e:
        raise serializers.ValidationError({"password": e.messages})


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def authenticate_user(self, request, **data):
        user = authenticate(request, **data)
        if not user:
            # TODO: Change to detail error
            raise serializers.ValidationError(
                {
                    "non_field_errors": [INVALID_CREDENTIALS_MSG],
                    "code": "invalid_credentials",
                }
            )
        return user

    def save(self):
        user = self.authenticate_user(self.context["request"], **self.validated_data)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return user


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128)

    def email_address_exists(self, email):
        user_exists = User.objects.filter(email__iexact=email).exists()
        return user_exists

    def validate_email(self, value):
        if self.email_address_exists(value):
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def save(self):
        email = self.validated_data["email"]
        password = self.validated_data["password"]

        user = User(email=email)
        user.set_password(password)
        validate_user_password_attribute_similarity(password, user)
        user.save()
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number1",
            "phone_number2",
            "gender",
            "title",
            "marital_status",
            "address1",
            "address2",
            "status",
            "type",
            "date_joined",
        ]


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "phone_number1",
            "phone_number2",
            "gender",
            "title",
            "marital_status",
            "address1",
            "address2",
            "type",
        ]

    def update(self):
        if self.validated_data["type"] == UserType.ADMIN:
            raise ValidationError({"detail": "Kindly contact admin."})

        user = User.objects.filter(pk=self.context["pk"])
        user.update(**self.validated_data)
        return user.first()


class UserDetailsTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserDetailsSerializer()
