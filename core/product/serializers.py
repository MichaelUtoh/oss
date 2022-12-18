from django.db import transaction
from django.db.models.functions import JSONObject

from rest_framework import serializers

from core.accounts.serializers import UserDetailsSerializer
from core.business.serializers import BusinessBasicSerializer
from core.config.serializers import IdListSerializer
from core.config.utils import generate_code
from core.product.models import Cart, OrderItem, Product, ProductImage


class ProductImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "name", "url", "created_at"]


class ProductQtySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class ProductListSerializer(serializers.ModelSerializer):
    business = BusinessBasicSerializer()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_no",
            "description",
            "category",
            "unit",
            "price",
            "tax",
            "business",
            "images",
        ]

    def get_images(self, obj):
        return ProductImage.objects.filter(product=obj).values(
            "id", "name", "url", "created_at"
        )


class ProductBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_no",
            "description",
            "category",
            "quantity",
            "unit",
            "price",
            "tax",
            "created_at",
        ]


class ProductInCartSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ["name", "price", "product_no", "description"]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "product_no",
            "description",
            "unit",
            "price",
            "tax",
        ]

    def to_representation(self, instance):
        return ProductListSerializer(instance=instance, context=self.context).data


class OrderItemListSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer()
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "customer", "product", "quantity", "price", "created_at"]

    def get_price(self, obj):
        return obj.get_item_price()


class OrderItemCreateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = OrderItem
        fields = ["quantity"]

    def save(self):
        existing_item = OrderItem.objects.filter(
            customer=self.context["customer"],
            product=self.context["product"],
        ).exists()

        if existing_item:
            item = OrderItem.objects.filter(
                customer=self.context["customer"],
                product=self.context["product"],
            ).first()
            item.quantity = self.validated_data["quantity"]
            item.save(update_fields=["quantity"])
            return item

        item = OrderItem.objects.create(
            customer=self.context["customer"],
            product=self.context["product"],
            quantity=self.validated_data["quantity"],
        )
        return item

    def to_representation(self, instance):
        return OrderItemListSerializer(instance=instance, context=self.context).data


class ItemBasicSerializer(serializers.Serializer):
    name = serializers.CharField(source="product__name")
    price = serializers.FloatField(source="product__price")
    tax = serializers.IntegerField(source="product__tax")
    quantity = serializers.IntegerField()


class CartListSerializer(serializers.Serializer):
    customer = serializers.SerializerMethodField()
    items = ItemBasicSerializer()
    total = serializers.SerializerMethodField()

    def get_queryset(self):
        customer = self.context["customer"]
        return Cart.objects.filter(items__customer=customer)

    def get_customer(self, obj):
        return self.context["customer"].get_full_name()

    def get_items(self, obj):
        # return self.get_queryset()[0].items.all().values("product__name", "product__price", "product__tax", "quantity")
        qs = self.get_queryset()[0].items.all()
        values = []

        for item in qs:
            print(item)
        #     item.annotate(json_object=JSONObject(
        #         name="product__name",
        #         price="product__price",
        #         tax="product__tax",
        #         quantity="quantity"
        #     ))
        #     values.append(item.json_object)

        return values

    def get_total(self, obj):
        return sum([i.get_item_price() for i in self.get_queryset()[0].items.all()])

    # TODO Calculate added Tax for Items in cart


class CartCreateUpdateSerializer(serializers.ModelSerializer):
    items = IdListSerializer

    class Meta:
        model = Cart
        fields = ["items"]

    def save(self):
        with transaction.atomic():
            mssg = "Add products to cart before proceeding"
            cart_exists = Cart.objects.filter(items__customer=self.context["customer"])
            if cart_exists:
                raise serializers.ValidationError({"detail": "You have a created Cart"})

            print()
            for i in self.validated_data["items"]:
                if not i.customer == self.context["customer"]:
                    raise serializers.ValidationError({"detail": mssg})

            cart = Cart.objects.create(
                code=generate_code(),
                total=sum([i.get_item_price() for i in self.validated_data["items"]]),
            )
            for i in self.validated_data["items"]:
                cart.items.add(i.id)
            return cart
