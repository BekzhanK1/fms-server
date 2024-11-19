from rest_framework import serializers

from farms.models import Farm
from farms.serializers import BriefFarmSerializer
from market.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ProductCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    farm = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all())

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "description",
            "price",
            "stock_quantity",
            "farm",
        ]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    farm = BriefFarmSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "description",
            "price",
            "stock_quantity",
            "farm",
        ]
        read_only_fields = ["id"]
