import functools
from django.http.response import JsonResponse

from rest_framework import viewsets


def server_error(request, *args, **kwargs):
    return JsonResponse({"detail": "Server Error(500)"}, status=500)


def not_found(request, exception, *args, **kwargs):
    return JsonResponse({"detail": "Not found"}, status=404)


def filter_http_method_names(method_list: list):
    # TODO: Add assertion for invalid methods
    return [
        method
        for method in viewsets.ModelViewSet.http_method_names
        if method not in method_list
    ]
