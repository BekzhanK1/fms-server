from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    CustomTokenObtainPairView,
    ProfileView,
    RegistrationView,
    SwitchRoleView,
    SocialsViewSet,
    UserViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"socials", SocialsViewSet, basename="socials")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("switch-role/", SwitchRoleView.as_view(), name="switch_role"),
    path("", include(router.urls)),
]
