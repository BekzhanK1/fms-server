from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Application, Farm


class BriefFarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "address",
            "geo_loc",
            "is_verified",
        ]
        read_only_fields = [
            "id",
            "name",
            "address",
            "geo_loc",
            "is_verified",
        ]


class FarmSerializer(serializers.ModelSerializer):
    farmer = UserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField(read_only=True)

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
            "is_owner",
        ]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at", "farmer"]

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request:
            return obj.farmer == request.user
        return False


class ApplicationSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)

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

    def validate(self, data):
        status_value = data.get("status")
        rejection_reason = data.get("rejection_reason")
        if status_value == "rejected" and not rejection_reason:
            raise serializers.ValidationError(
                {
                    "rejection_reason": "Rejection reason is required when status is 'rejected'."
                }
            )
        return data
