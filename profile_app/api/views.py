from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    ProfileSerializer,
)

User = get_user_model()


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Show any profile and let the owner update it.

    The pk in the URL is the user id.
    """

    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    http_method_names = ['get', 'patch']


class BusinessProfileListView(generics.ListAPIView):
    """List all business users."""

    queryset = User.objects.filter(type='business')
    serializer_class = BusinessProfileListSerializer


class CustomerProfileListView(generics.ListAPIView):
    """List all customers."""

    queryset = User.objects.filter(type='customer')
    serializer_class = CustomerProfileListSerializer
