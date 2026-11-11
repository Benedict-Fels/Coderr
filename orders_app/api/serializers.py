from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order

SNAPSHOT_FIELDS = [
    'title', 'revisions', 'delivery_time_in_days', 'price', 'features',
    'offer_type',
]


class OrderSerializer(serializers.ModelSerializer):
    """Full order; only the status can be changed."""

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', *SNAPSHOT_FIELDS,
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'customer_user', 'business_user', *SNAPSHOT_FIELDS,
        ]

    def validate(self, data):
        """Reject every field except status."""
        not_allowed = set(self.initial_data) - {'status'}
        if not_allowed:
            raise serializers.ValidationError(
                f'Nur der Status darf geändert werden: {sorted(not_allowed)}')
        if 'status' not in data:
            raise serializers.ValidationError(
                {'status': 'Dieses Feld ist erforderlich.'})
        return data


class OrderCreateSerializer(serializers.Serializer):
    """Create an order as a snapshot of an offer detail."""

    offer_detail_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        """Copy the detail's data and set customer and business user."""
        detail = get_object_or_404(
            OfferDetail.objects.select_related('offer'),
            id=validated_data['offer_detail_id'],
        )
        snapshot = {field: getattr(detail, field) for field in SNAPSHOT_FIELDS}
        return Order.objects.create(
            customer_user=validated_data['customer_user'],
            business_user=detail.offer.user,
            **snapshot,
        )

    def to_representation(self, instance):
        """Return the created order in its full form."""
        return OrderSerializer(instance).data
