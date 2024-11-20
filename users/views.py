from django.db import IntegrityError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from users.models import Social, User
from users.permissions import IsAdmin, IsFarmer
from users.serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from users.service import create_if_not_exists
from .serializers import (
    AdminUserSerializer,
    RegistrationSerializer,
    SocialSerializer,
    UpdateUserSerializer,
    UserSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.all()


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user: User = serializer.save()
                create_if_not_exists(user)
                return Response(
                    {"message": "User registered successfully", "user_id": user.id},
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {"error": "A database error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        try:
            user: User = request.user
            serializer = self.serializer_class(user, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        try:
            user: User = request.user
            delivery_address = request.data.get("delivery_address")
            payment_method = request.data.get("payment_method")
            if delivery_address and payment_method:
                buyer_info = user.buyer_info
                buyer_info.payment_method = payment_method
                buyer_info.delivery_address = delivery_address
                buyer_info.save()
            else:
                return Response(
                    {"error": "Both delivery_address and payment_method are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = UpdateUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                serializer = self.serializer_class(user, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SwitchRoleView(APIView):
    serializer_class = UserSerializer

    def put(self, request):
        user: User = request.user
        try:
            if not hasattr(user, "switch_role"):
                raise AttributeError(
                    "The switch_role method is not implemented on the User model."
                )
            user.switch_role()
            create_if_not_exists(user)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AttributeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SocialsViewSet(viewsets.ModelViewSet):
    queryset = Social.objects.all()
    serializer_class = SocialSerializer
    permission_classes = [IsFarmer]

    def get_queryset(self):
        return Social.objects.filter(farmer=self.request.user)

    def perform_create(self, serializer):
        if Social.objects.filter(farmer=self.request.user).count() >= 5:
            raise PermissionDenied("You can only have 5 social links.")
        serializer.save(farmer=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.farmer != self.request.user:
            raise PermissionDenied(
                "You do not have permission to update this social link."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.farmer != self.request.user:
            raise PermissionDenied(
                "You do not have permission to delete this social link."
            )
        instance.delete()
