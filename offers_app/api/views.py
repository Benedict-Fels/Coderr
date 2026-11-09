from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter

from offers_app.models import Offer, OfferDetail
from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessOrReadOnly
from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
)


def offers_with_min_values():
    """Return all offers with min_price and min_delivery_time attached."""
    return (
        Offer.objects
        .select_related('user')
        .prefetch_related('details')
        .annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        )
    )


class OfferListCreateView(generics.ListCreateAPIView):
    """List offers for everyone, let business users create new ones."""

    permission_classes = [IsBusinessOrReadOnly]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return the offers including their computed minimum values."""
        return offers_with_min_values()

    def get_serializer_class(self):
        """Use the create serializer for POST, the list one otherwise."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        """Save the logged-in user as creator, never the request body."""
        serializer.save(user=self.request.user)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Show a single offer detail to logged-in users."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
