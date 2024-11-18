from rest_framework.permissions import BasePermission


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
