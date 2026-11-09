from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail

User = get_user_model()

REQUIRED_OFFER_TYPES = {'basic', 'standard', 'premium'}


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of a single offer detail."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 'price',
            'features', 'offer_type',
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Short representation of an offer detail: its id and URL."""

    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail')

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class UserDetailsSerializer(serializers.ModelSerializer):
    """Public name data of the user who created an offer."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
    """Offer as shown in the list, with values computed from its details.

    min_price and min_delivery_time are annotated by the queryset.
    """

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at',
            'updated_at', 'details', 'min_price', 'min_delivery_time',
            'user_details',
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    """Create an offer together with its three details in one request."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        """Require exactly one basic, one standard and one premium detail."""
        if len(value) != 3:
            raise serializers.ValidationError(
                'Ein Angebot muss genau 3 Details enthalten.')
        offer_types = {detail['offer_type'] for detail in value}
        if offer_types != REQUIRED_OFFER_TYPES:
            raise serializers.ValidationError(
                'Es muss je ein Detail vom Typ basic, standard und '
                'premium geben.')
        return value

    def create(self, validated_data):
        """Save the offer and its details: either everything or nothing."""
        details_data = validated_data.pop('details')
        with transaction.atomic():
            offer = Offer.objects.create(**validated_data)
            for detail_data in details_data:
                OfferDetail.objects.create(offer=offer, **detail_data)
        return offer
