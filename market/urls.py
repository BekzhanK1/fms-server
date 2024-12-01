from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BasketItemViewSet,
    BasketViewSet,
    CategoryViewSet,
    OrderViewSet,
    ProductViewSet,
    FarmerOrderViewSet,
)

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"basket-items", BasketItemViewSet, basename="basket-item")
router.register(r"basket", BasketViewSet, basename="basket")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"farmer-orders", FarmerOrderViewSet, basename="farmer-order")

urlpatterns = [
    path("", include(router.urls)),
]
