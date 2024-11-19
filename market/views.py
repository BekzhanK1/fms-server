from farms.models import Application, Farm
from farms.serializers import ApplicationSerializer, FarmSerializer
from market.models import Basket, BasketItem, Category, Product
from market.serializers import (
    BasketItemCreateSerializer,
    BasketItemSerializer,
    BasketSerializer,
    CategorySerializer,
    ProductCreateSerializer,
    ProductSerializer,
)
from users.models import Social, User
from users.permissions import IsAdmin, IsBuyer, IsFarmer, IsFarmerOrReadOnly
from users.serializers import CustomTokenObtainPairSerializer
from users.choices import Role
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != Role.Admin:
            raise PermissionDenied("Only admins can create categories.")

        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Restrict updates to admins.
        """
        if request.user.role != Role.Admin:
            raise PermissionDenied("Only admins can update categories.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Restrict deletion to admins.
        """
        if request.user.role != Role.Admin:
            raise PermissionDenied("Only admins can delete categories.")
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating, retrieving, listing, updating, and deleting products.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsFarmerOrReadOnly]

    def get_queryset(self):
        return Product.objects.filter(farm__is_verified=True)

    def perform_create(self, serializer):
        serializer = ProductCreateSerializer(data=self.request.data)

        if self.request.user.role != "Farmer":
            raise PermissionDenied("Only farmers can create products.")

        farm = Farm.objects.get(id=self.request.data["farm"])

        if farm.farmer != self.request.user:
            raise PermissionDenied(
                "You do not have permission to create a product for this farm."
            )

        if serializer.is_valid():
            serializer.save(farm=farm)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Restrict updates to the product owner.
        """
        product = self.get_object()
        farm = Farm.objects.get(id=product.farm.id)

        if farm.farmer != request.user:
            raise PermissionDenied("You do not have permission to update this product.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Restrict deletion to the product owner.
        """
        product = self.get_object()
        farm = Farm.objects.get(id=product.farm.id)

        if farm.farmer != request.user:
            raise PermissionDenied("You do not have permission to update this product.")
        return super().destroy(request, *args, **kwargs)


class BasketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing the user's basket.
    Users can retrieve or list their baskets but cannot create or delete them.
    Clearing the basket items is allowed via a custom action.
    """

    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_queryset(self):
        """
        Restrict the queryset to the authenticated user's basket.
        """
        return Basket.objects.filter(buyer=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Disable the ability to delete the basket.
        """
        raise PermissionDenied("You cannot delete the basket.")

    @action(detail=False, methods=["post"], url_path="clear")
    def clear_basket(self, request):
        """
        Custom action to clear the user's basket items.
        """
        basket = self.get_queryset().first()
        if not basket:
            return Response(
                {"detail": "Basket not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        BasketItem.objects.filter(basket=basket).delete()
        return Response(
            {"detail": "Basket cleared successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class BasketItemViewSet(viewsets.ModelViewSet):
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_queryset(self):
        """
        Restrict the queryset to the authenticated user's basket items.
        """
        return BasketItem.objects.filter(basket__buyer=self.request.user)

    def list(self, request):
        return Response(
            {
                "error": "You can only create, retrieve, update, and delete basket items."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def create(self, request):
        serializer = BasketItemCreateSerializer(data=self.request.data)
        basket, created = Basket.objects.get_or_create(buyer=self.request.user)
        product_id = self.request.data.get("product")
        quantity = self.request.data.get("quantity")

        if not product_id or not quantity:
            raise PermissionDenied("Product and quantity are required.")

        product = Product.objects.get(id=product_id)

        if product.stock_quantity < int(quantity):
            raise PermissionDenied("Not enough stock available.")

        basket_item = BasketItem.objects.filter(basket=basket, product=product).first()
        if basket_item:
            print(
                f"You have {basket_item.quantity} of this item in your basket. Adding {quantity} more."
            )
            basket_item.quantity += quantity
            basket_item.save()
            return Response(
                BasketItemSerializer(basket_item).data, status=status.HTTP_200_OK
            )

        if serializer.is_valid():
            basket_item = serializer.save(
                basket=basket, product=product, quantity=quantity
            )
            return Response(
                BasketItemSerializer(basket_item).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        basket_item = self.get_object()
        if basket_item.basket.buyer != request.user:
            raise PermissionDenied(
                "You do not have permission to update this basket item."
            )
        quantity = request.data.get("quantity")
        if quantity:
            product = basket_item.product
            if product.stock_quantity < quantity:
                raise PermissionDenied("Not enough stock available.")
            else:
                basket_item.quantity = quantity
                basket_item.save()
        return Response(
            BasketItemSerializer(basket_item).data, status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """
        Restrict deletion to the basket item owner.
        """
        basket_item = self.get_object()
        if basket_item.basket.buyer != request.user:
            raise PermissionDenied(
                "You do not have permission to delete this basket item."
            )
        return super().destroy(request, *args, **kwargs)
