from rest_framework import serializers

from farms.models import Farm
from farms.serializers import BriefFarmSerializer
from users.serializers import BuyerSerializer
from market.models import Basket, BasketItem, Category, Order, OrderItem, Product


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


class FarmProductSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["id"]


class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = BasketItem
        fields = ["id", "product", "quantity"]
        read_only_fields = ["id"]


class BasketItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = BasketItem
        fields = ["id", "product", "quantity"]
        read_only_fields = ["id"]


class BasketSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Basket
        fields = ["id", "buyer", "items", "total_price", "created_at"]
        read_only_fields = ["id", "buyer", "created_at"]

    def get_items(self, obj):
        return BasketItemSerializer(obj.items.all(), many=True).data

    def get_total_price(self, obj):
        return obj.total_price


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]
        read_only_fields = ["id"]


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    buyer = BuyerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "buyer", "items", "total_price", "created_at"]
        read_only_fields = ["id", "buyer", "created_at"]

    def get_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total_price(self, obj):
        return obj.total_price
