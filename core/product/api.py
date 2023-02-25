import csv
import io
import math

from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404

import cloudinary
import cloudinary.uploader
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pyqrcode import QRCode
from rest_framework import (
    filters,
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

from core.cart.models import Cart, CartItem
from core.config.choices import UserType
from core.business.models import Business
from core.product.models import ProductImage
from core.config.permissions import (
    AdminOnlyPermission,
    BusinessOwnerPermission,
    CustomerPermission,
)
from core.accounts.models import User
from core.cart.serializers import CartItemCreateUpdateSerializer, CartListSerializer
from core.config.schema import get_auto_schema_class_by_tags
from core.config.utils import generate_code
from core.product.models import Product, ProductFavorite
from core.product.serializers import (
    ProductBasicSerializer,
    ProductCreateUpdateSerializer,
    ProductFavoriteListSerializer,
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

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return ProductCreateUpdateSerializer
        if self.action in ["list", "retrieve"]:
            return ProductBasicSerializer

    def get_business(self):
        return Business.objects.filter(pk=self.kwargs["business_pk"])

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
        business = get_object_or_404(Business, pk=self.kwargs["business_pk"])

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
                    "unit": data[4],
                    "price": data[5],
                    "tax": data[6] or 0,
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
        products = self.get_queryset().filter(
            business__owner=request.user, business_id=self.kwargs["business_pk"]
        )

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


class ProductFavoriteViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ProductFavorite.objects.all()
    swagger_schema = get_auto_schema_class_by_tags(["products"])
    permission_classes = [CustomerPermission]

    @swagger_auto_schema(
        request_body=None,
        responses={status.HTTP_200_OK: None},
    )
    def create(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["id"])

        if ProductFavorite.objects.filter(user=request.user, product=product).exists():
            ProductFavorite.objects.filter(user=request.user, product=product).delete()
            return Response(status=status.HTTP_200_OK)

        ProductFavorite.objects.create(user=request.user, product=product)
        return Response(status=status.HTTP_200_OK)


class ProductBasicViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = (
        Product.objects.all().prefetch_related("business", "discount").order_by("-name")
    )
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "category", "description" "product_no"]

    def get_serializer_class(self):
        if self.action == "add_to_cart":
            return CartItemCreateUpdateSerializer
        if self.action == "list":
            return ProductListSerializer

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: ProductListSerializer}
    )
    @action(detail=False, methods=["get"])
    def favorites(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            msg = "Sign in to create or view your favorite products"
            raise serializers.ValidationError({"detail": msg})

        items = get_list_or_404(ProductFavorite, user=request.user)
        data = ProductFavoriteListSerializer(items, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CartItemCreateUpdateSerializer)
    @action(detail=False, methods=["post"])
    def add_to_cart(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: ProductListSerializer}
    )
    def list(self, request, *args, **kwargs):
        search_q = request.GET.get("search")
        qs = (
            (
                self.get_queryset().filter(
                    Q(name__icontains=search_q)
                    | Q(product_no__icontains=search_q)
                    | Q(description__icontains=search_q)
                    | Q(category__icontains=search_q)
                )
            )
            if search_q
            else self.get_queryset()
        )

        data = self.get_serializer(qs, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class ProductImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
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
        user = request.user
        file = request.FILES.get("file")
        product = get_object_or_404(Product, pk=self.kwargs["id"])
        if not product.business.owner == user:
            raise serializers.ValidationError({"detail": "Not allowed"})

        if ProductImage.objects.filter(name=str(file)).exists():
            msg = "Image with the same name already exists"
            raise serializers.ValidationError({"detail": msg})

        res = cloudinary.uploader.upload(file.file)
        url = res.get("url")

        image = ProductImage(product=product, name=str(file), url=url)
        image.save()
        data = ProductImageListSerializer(image).data
        return Response(data=data, status=status.HTTP_200_OK)
