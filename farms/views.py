from farms.models import Application, Farm
from farms.serializers import ApplicationSerializer, FarmSerializer
from users.models import Social, User
from users.permissions import IsAdmin, IsFarmer, IsFarmerOrReadOnly
from users.serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class FarmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating, retrieving, listing, updating, and deleting farms.
    """

    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, IsFarmerOrReadOnly]

    def get_queryset(self):
        """
        Customize queryset based on the user role.
        - Farmers see their own farms.
        - Others can view all farms.
        """
        return Farm.objects.filter(is_verified=True)

    def perform_create(self, serializer):
        """
        Automatically assign the authenticated user as the farmer when creating a farm.
        """
        if self.request.user.role != "Farmer":
            raise PermissionDenied("Only farmers can create farms.")
        serializer.save(farmer=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Restrict updates to the farm owner.
        """
        farm = self.get_object()
        if farm.farmer != request.user:
            raise PermissionDenied("You do not have permission to update this farm.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Restrict deletion to the farm owner.
        """
        farm = self.get_object()
        if farm.farmer != request.user:
            raise PermissionDenied("You do not have permission to delete this farm.")
        return super().destroy(request, *args, **kwargs)


class ApplicationView(APIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        query_params = request.query_params
        status_filter = query_params.get("status")

        if status_filter in ["pending", "approved", "rejected"]:
            applications = Application.objects.filter(status=status_filter)
        elif pk:
            try:
                application = Application.objects.get(pk=pk)
                serializer = self.serializer_class(application)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Application.DoesNotExist:
                return Response(
                    {"detail": "Application not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            applications = Application.objects.all()

        serializer = self.serializer_class(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            application = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response(
                {"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data
        status_value = data.get("status")
        rejection_reason = data.get("rejection_reason")

        if status_value == "rejected" and not rejection_reason:
            return Response(
                {"detail": "Rejection reason is required when status is 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(application, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
