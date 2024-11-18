from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsFarmer(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_farmer
        )


class IsBuyer(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_buyer
        )


class IsFarmerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and obj.farmer == request.user
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_admin
        )
