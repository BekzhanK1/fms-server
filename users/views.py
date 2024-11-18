
from django.db import IntegrityError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from users.models import User
from users.serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, UpdateUserSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    {"message": "User registered successfully", "user_id": user.id},
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response({"error": "A database error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    serializer_class = UserSerializer
    def get(self, request):
        try:
            user: User = request.user
            serializer = self.serializer_class(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            user: User = request.user
            serializer = UpdateUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                serializer = self.serializer_class(user, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
class SwitchRoleView(APIView):
    serializer_class = UserSerializer
    def put(self, request):
        user: User = request.user
        try:
            if not hasattr(user, 'switch_role'):
                raise AttributeError("The switch_role method is not implemented on the User model.")
            user.switch_role()
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AttributeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
        
        
    