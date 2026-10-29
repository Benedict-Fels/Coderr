from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    ProfileSerializer, BusinessProfileListSerializer, CustomerProfileListSerializer,
)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = 'user'
    lookup_url_kwarg = 'pk'
    http_method_names = ['get', 'patch']


class BusinessProfileListView(generics.ListAPIView):
    queryset = Profile.objects.filter(type='business').select_related('user')
    serializer_class = BusinessProfileListSerializer


class CustomerProfileListView(generics.ListAPIView):
    queryset = Profile.objects.filter(type='customer').select_related('user')
    serializer_class = CustomerProfileListSerializer
