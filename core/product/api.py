import csv
import io
import math
import pandas as pd

from django.db.models import Q

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pyqrcode import QRCode
from rest_framework import generics, mixins, parsers, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.business.models import Business
from core.config.choices import UserType
from core.config.permissions import (
    AdminOnlyPermission,
    BusinessOwnerPermission,
    CustomerPermission,
)
from core.config.schema import get_auto_schema_class_by_tags
from core.product.models import Product
from core.product.serializers import (
    ProductBasicSerializer,
    ProductCreateUpdateSerializer,
    ProductListSerializer,
)


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Product.objects.all().order_by("name")
    swagger_schema = get_auto_schema_class_by_tags(["businesses"])
    permission_classes = [BusinessOwnerPermission | AdminOnlyPermission]

    def get_business(self):
        return Business.objects.filter(pk=self.kwargs["business_pk"])

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return ProductCreateUpdateSerializer
        if self.action in ["list", "retrieve"]:
            return ProductBasicSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Document",
            )
        ],
        responses={400: "Invalid data in uploaded file", 200: "Success"},
    )
    @action(
        detail=False,
        methods=["post"],
        parser_classes=(MultiPartParser,),
        name="batch_upload",
        url_path="batch_upload",
    )
    def batch(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        try:
            business = Business.objects.filter(pk=self.kwargs["business_pk"]).first()
        except Business.DoesNotExist:
            msg = "Not found"
            raise serializers.ValidationError({"detail": msg})

        if not file.name.endswith(".csv"):
            msg = "Wrong format! Make sure its a CSV(.csv) file."
            raise serializers.ValidationError({"detail": msg})

        decoded_file = file.read().decode()
        io_string = io.StringIO(decoded_file)
        csv_reader = csv.reader(io_string, delimiter=",")
        file.close()

        line_count = 0
        product_list = []
        for data in csv_reader:
            if line_count == 0:
                line_count += 1
                continue

            serializer = ProductCreateUpdateSerializer(
                data={
                    "name": data[0],
                    "product_no": data[1],
                    "description": data[2],
                    "category": data[3],
                    "quantity": data[4],
                    "unit": data[5],
                    "price": data[6],
                    "tax": data[7] or 0,
                }
            )

            serializer.is_valid(raise_exception=True)

            if Product.objects.filter(name=data[0], product_no=data[1]).exists():
                msg = f"Product record in {line_count} already exists"
                raise serializers.ValidationError({"detail": msg})

            product = Product(business=business, **serializer.validated_data)
            product_list.append(product)

        Product.objects.bulk_create(product_list)
        return Response()

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: ProductListSerializer})
    def create(self, request, *args, **kwargs):
        business = self.get_business().first()

        if Product.objects.filter(
            name=request.data["name"], product_no=request.data["product_no"]
        ).exists():
            raise serializers.ValidationError(
                {"detail": "Product with the given information already exists"}
            )

        product = Product.objects.create(**request.data, business=business)
        data = ProductBasicSerializer(product).data
        return Response(data=data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="number of data in a page",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="param to get products by name",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 100))
        offset = (page - 1) * limit if page > 1 else 0
        search = request.GET.get("search")
        products = self.get_queryset().filter(business__owner=request.user)

        if search:
            products = products.filter(
                Q(name__icontains=search)
                | Q(product_no__icontains=search)
                | Q(description__icontains=search)
            )

        data = self.get_serializer(products, many=True).data

        total_count = len(data)
        total_pages = total_count / limit
        if int(total_pages) == 0:
            total_pages = 0
        elif int(total_pages) < 1:
            total_pages = 1
        else:
            total_pages = math.ceil(total_pages)
        return Response(
            {
                "count": total_count,
                "total_pages": total_pages,
                "data": data[offset : offset + limit],
            }
        )

    def update(self, request, *args, **kwargs):
        business = self.get_business().first()
        product = Product.objects.filter(business=business, pk=self.kwargs["pk"])
        product.update(business=business, **request.data)
        product = product.first()
        data = ProductBasicSerializer(product).data
        return Response(data=data)


class ProductBasicViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all().order_by("-name")
    serializer_class = ProductListSerializer
    permission_classes = [CustomerPermission]
