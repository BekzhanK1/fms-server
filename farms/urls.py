from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplicationView, FarmViewSet

router = DefaultRouter()
router.register(r"farms", FarmViewSet, basename="farm")

urlpatterns = [
    path("", include(router.urls)),
    path("applications/", ApplicationView.as_view(), name="applications"),
]
