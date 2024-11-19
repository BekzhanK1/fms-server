from farms.models import Application, Farm
from farms.serializers import ApplicationSerializer, FarmSerializer
from market.models import Product
from market.serializers import ProductCreateSerializer, ProductSerializer
from users.models import Social, User
from users.permissions import IsAdmin, IsFarmer, IsFarmerOrReadOnly
from users.serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied


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
