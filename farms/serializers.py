from rest_framework import serializers

from farms.utils import calculate_distance
from users.serializers import UserSerializer
from .models import Application, Farm


class BriefFarmSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Farm
        fields = ["id", "name", "address", "is_verified", "distance"]
        read_only_fields = ["id", "name", "address", "is_verified", "distance"]

    def get_distance(self, obj):
        request = self.context.get("request")
        if not obj.latitude or not obj.longitude:
            return None

        farm_location = (obj.latitude, obj.longitude)

        if request:
            latitude = request.query_params.get("latitude")
            longitude = request.query_params.get("longitude")

            if latitude and longitude:
                try:
                    user_location = (float(latitude), float(longitude))
                    return round(calculate_distance(user_location, farm_location), 2)
                except ValueError:
                    return None

        return None


class FarmSerializer(serializers.ModelSerializer):
    farmer = UserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField(read_only=True)
    distance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "address",
            "size",
            "crop_types",
            "is_verified",
            "latitude",
            "longitude",
            "distance",
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

    def get_distance(self, obj):
        request = self.context.get("request")
        if not obj.latitude or not obj.longitude:
            return None

        farm_location = (obj.latitude, obj.longitude)

        if request:
            latitude = request.query_params.get("latitude")
            longitude = request.query_params.get("longitude")

            if latitude and longitude:
                try:
                    user_location = (float(latitude), float(longitude))
                    return round(calculate_distance(user_location, farm_location), 2)
                except ValueError:
                    return None

        return None


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
