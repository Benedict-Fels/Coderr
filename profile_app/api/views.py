from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    ProfileSerializer, BusinessProfileListSerializer, CustomerProfileListSerializer,
)

User = get_user_model()


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    # <pk> in der URL ist jetzt einfach die User-ID -> kein lookup_field mehr nötig
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    http_method_names = ['get', 'patch']


class BusinessProfileListView(generics.ListAPIView):
    queryset = User.objects.filter(type='business')
    serializer_class = BusinessProfileListSerializer


class CustomerProfileListView(generics.ListAPIView):
    queryset = User.objects.filter(type='customer')
    serializer_class = CustomerProfileListSerializer
