import django_filters

from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Query parameters for the offer list.

    min_price and min_delivery_time refer to the values annotated
    by the view's queryset.
    """

    creator_id = django_filters.NumberFilter(field_name='user_id')
    min_price = django_filters.NumberFilter(
        field_name='min_price', lookup_expr='gte')
    max_delivery_time = django_filters.NumberFilter(
        field_name='min_delivery_time', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = []
