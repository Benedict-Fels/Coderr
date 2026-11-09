from rest_framework import generics

from offers_app.models import Offer
from .permissions import IsBusinessOrReadOnly
from .serializers import OfferCreateSerializer


class OfferListCreateView(generics.CreateAPIView):
    """Create offers. The GET list follows in the next step."""

    queryset = Offer.objects.all()
    serializer_class = OfferCreateSerializer
    permission_classes = [IsBusinessOrReadOnly]

    def perform_create(self, serializer):
        """Save the logged-in user as creator, never the request body."""
        serializer.save(user=self.request.user)
