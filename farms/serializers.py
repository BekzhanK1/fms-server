from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Application, Farm


class FarmSerializer(serializers.ModelSerializer):
    farmer = UserSerializer()

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "address",
            "geo_loc",
            "size",
            "crop_types",
            "is_verified",
            "created_at",
            "updated_at",
            "farmer",
        ]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at", "farmer"]


class ApplicationSerializer(serializers.ModelSerializer):
    farm = FarmSerializer()

    class Meta:
        model = Application
        fields = [
            "id",
            "farm",
            "status",
            "rejection_reason",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "created_at",
        ]