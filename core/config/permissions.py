from rest_framework import permissions

from core.config.choices import UserType


def is_customer(request):
    if not request.user.is_authenticated:
        return False

    if request.user.type == UserType.CUSTOMER:
        return True


def is_business_owner(request):
    if not request.user.is_authenticated:
        return False

    if request.user.type == UserType.SHOP_OWNER:
        return True


def is_admin_only(request):
    if not request.user.is_authenticated:
        return False

    if request.user.type == UserType.ADMIN:
        return True


class CustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_customer(request):
            return True
        return False


class BusinessOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_business_owner(request):
            return True
        return False


class AdminOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_admin_only(request):
            return True
        return False
