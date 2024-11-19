from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from users.models import Social, User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_role(self, value):
        if value == "Admin":
            raise serializers.ValidationError("Role cannot be Admin.")
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()
    socials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
            "info",
            "socials",
        ]
        read_only_fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
        ]

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def get_info(self, obj):
        if obj.role == "Farmer":
            farmer_info = getattr(obj, "farmer_info", None)
            if farmer_info:
                return {
                    "rating": farmer_info.rating,
                    "experience": farmer_info.experience,
                    "bio": farmer_info.bio,
                }
        elif obj.role == "Buyer":
            buyer_info = getattr(obj, "buyer_info", None)
            if buyer_info:
                return {
                    "delivery_address": buyer_info.delivery_address,
                    "payment_method": buyer_info.payment_method,
                }
        return None

    def get_socials(self, obj):
        socials = Social.objects.filter(farmer=obj)
        return SocialSerializer(socials, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.role == "Buyer":
            representation.pop("socials", None)
        return representation


class BuyerSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
            "info",
        ]
        read_only_fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
        ]

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def get_info(self, obj):
        buyer_info = getattr(obj, "buyer_info", None)
        if buyer_info:
            return {
                "delivery_address": buyer_info.delivery_address,
                "payment_method": buyer_info.payment_method,
            }
        return None


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone": {"required": False},
            "avatar": {"required": False},
        }

    def update(self, instance: User, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = ["id", "platform", "url"]
        read_only_fields = ["id"]

    def validate_url(self, value):
        if not value.startswith("http"):
            raise serializers.ValidationError("The URL must start with http or https.")
        return value
