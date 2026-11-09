from rest_framework import generics

from offers_app.models import Offer
from .permissions import IsBusinessOrReadOnly
from .serializers import OfferCreateSerializer


class OfferListCreateView(generics.CreateAPIView):
    """Create offers. The GET list will be added in the next step."""

    queryset = Offer.objects.all()
    serializer_class = OfferCreateSerializer
    permission_classes = [IsBusinessOrReadOnly]

    def perform_create(self, serializer):
        """Set the logged-in user as creator instead of trusting the request body."""
        serializer.save(user=self.request.user)
