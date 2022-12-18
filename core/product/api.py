import csv
import io
import math
import pandas as pd

from django.db.models import Q
from django.shortcuts import get_object_or_404

import cloudinary
import cloudinary.uploader
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pyqrcode import QRCode
from rest_framework import (
    filters,
    generics,
    mixins,
    parsers,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.accounts.models import User
from core.business.models import Business
from core.product.models import ProductImage
from core.config.choices import UserType
from core.config.permissions import (
    AdminOnlyPermission,
    BusinessOwnerPermission,
    CustomerPermission,
)
from core.config.schema import get_auto_schema_class_by_tags
from core.product.models import Cart, OrderItem, Product, ProductFavorite
from core.product.serializers import (
    CartCreateUpdateSerializer,
    CartListSerializer,
    OrderItemCreateSerializer,
    OrderItemListSerializer,
    ProductBasicSerializer,
    ProductCreateUpdateSerializer,
    ProductImageListSerializer,
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
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "category", "description" "product_no"]


class ProductImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    parser_classes = [MultiPartParser]
    permission_classes = [BusinessOwnerPermission]
    queryset = ProductImage.objects.all().select_related("product")

    def get_serializer_class(self):
        if self.action == "list":
            return ProductImageListSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Image",
            )
        ],
        request_body=None,
        responses={status.HTTP_200_OK: ProductImageListSerializer},
    )
    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        if ProductImage.objects.filter(name=str(file)).exists():
            msg = "Image with the same name already exists"
            raise serializers.ValidationError({"detail": msg})

        product = get_object_or_404(Product, pk=self.kwargs["product_pk"])
        res = cloudinary.uploader.upload(file.file)
        url = res.get("url")

        image = ProductImage(product=product, name=str(file), url=url)
        image.save()
        data = ProductImageListSerializer(image).data
        return Response(data=data, status=status.HTTP_200_OK)


class ProductImageListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = ProductImage.objects.all().select_related("product")
    serializer_class = ProductImageListSerializer

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: ProductImageListSerializer}
    )
    def list(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["product_pk"])
        images_qs = ProductImage.objects.filter(product=product)
        data = self.get_serializer(images_qs, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class OrderItemsViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = OrderItem.objects.all()
    swagger_schema = get_auto_schema_class_by_tags(["products"])
    permission_classes = [CustomerPermission]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderItemCreateSerializer

    @swagger_auto_schema(
        request_body=OrderItemCreateSerializer,
        responses={status.HTTP_200_OK: OrderItemListSerializer},
    )
    def create(self, request, *args, **kwargs):
        customer, product = request.user, get_object_or_404(
            Product, pk=self.kwargs["product_pk"]
        )
        serializer = self.get_serializer(
            data=request.data, context={"customer": customer, "product": product}
        )
        serializer.is_valid(raise_exception=True)
        order_item = serializer.save()
        data = self.get_serializer(instance=order_item).data
        return Response(data=data)


class ProductFavoriteViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ProductFavorite.objects.all()
    swagger_schema = get_auto_schema_class_by_tags(["products"])
    permission_classes = [CustomerPermission]

    @swagger_auto_schema(
        request_body=None,
        responses={status.HTTP_200_OK: None},
    )
    def create(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["product_pk"])

        if ProductFavorite.objects.filter(user=request.user, product=product).exists():
            ProductFavorite.objects.filter(user=request.user, product=product).delete()
            return Response(status=status.HTTP_200_OK)

        ProductFavorite.objects.create(user=request.user, product=product)
        return Response(status=status.HTTP_200_OK)


class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    swagger_schema = get_auto_schema_class_by_tags(["cart"])

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return CartCreateUpdateSerializer
        if self.action == "list":
            return CartListSerializer

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: CartListSerializer}
    )
    def list(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        serializer = self.get_serializer(data=request.data, context={"customer": user})
        serializer.is_valid(raise_exception=True)
        # cart = Cart.objects.filter(items__customer=user)
        # print(cart)
        # data = self.get_serializer(cart).data
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CartCreateUpdateSerializer,
        responses={status.HTTP_201_CREATED: CartListSerializer},
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={"customer": user})
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        data = CartListSerializer(cart).data
        return Response(data=data, status=status.HTTP_201_CREATED)
