from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

import debug_toolbar
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, routers

from core.accounts.api import UserDetailViewSet, UserLoginAPIView, UserRegisterAPIView
from core.business.api import BusinessViewSet, CouponViewSet
from core.marketing.api import EmailViewSet
from core.product.api import (
    CartViewSet,
    OrderItemsViewSet,
    ProductBasicViewSet,
    ProductViewSet,
    ProductFavoriteViewSet,
)


schema_view = get_schema_view(
    openapi.Info(
        title="OSS",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="michaelutoh21@gmail.com"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"auth/users", UserDetailViewSet, basename="users")
router.register(r"auth/users/(?P<user_pk>[\d]+)/cart", CartViewSet, basename="cart")
router.register(r"businesses", BusinessViewSet, basename="shops")
router.register(
    r"businesses/(?P<business_pk>[\d]+)/products",
    ProductViewSet,
    basename="products",
)
router.register(
    r"businesses/(?P<business_pk>[\d]+)/coupons",
    CouponViewSet,
    basename="coupons",
)
router.register(r"marketing", EmailViewSet, basename="marketing")
router.register(r"products", ProductBasicViewSet, basename="products")
router.register(
    r"products/(?P<product_pk>[\d]+)/add_to_cart",
    OrderItemsViewSet,
    basename="orders",
)
router.register(
    r"products/(?P<product_pk>[\d]+)/toggle_favorite",
    ProductFavoriteViewSet,
    basename="favorite",
)
urlpatterns = router.urls


urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        re_path(
            r"^redoc/$",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        re_path(r"auth/register", UserRegisterAPIView.as_view(), name="register"),
        re_path(r"auth/login", UserLoginAPIView.as_view(), name="login"),
        path("admin/", admin.site.urls),
        path("__debug__/", include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler500 = "core.config.services.server_error"
handler404 = "core.config.services.not_found"
