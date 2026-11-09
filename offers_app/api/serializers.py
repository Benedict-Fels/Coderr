from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of a single offer detail (basic, standard or premium)."""

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferCreateSerializer(serializers.ModelSerializer):
    """Create an offer together with its three details in one request."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        """Require exactly one basic, one standard and one premium detail."""
        if len(value) != 3:
            raise serializers.ValidationError('Ein Angebot muss genau 3 Details enthalten.')

        offer_types = {detail['offer_type'] for detail in value}
        if offer_types != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError(
                'Es muss genau je ein Detail vom Typ basic, standard und premium geben.')
        return value

    def create(self, validated_data):
        """Save the offer and its details atomically: either everything or nothing."""
        details_data = validated_data.pop('details')

        with transaction.atomic():
            offer = Offer.objects.create(**validated_data)
            for detail_data in details_data:
                OfferDetail.objects.create(offer=offer, **detail_data)

        return offer
