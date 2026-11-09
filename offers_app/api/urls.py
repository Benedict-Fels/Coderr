from django.urls import path

from .views import (
    OfferDetailRetrieveView,
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('offers/', OfferListCreateView.as_view()),
    path('offers/<int:pk>/', OfferRetrieveUpdateDestroyView.as_view()),
    path(
        'offerdetails/<int:pk>/',
        OfferDetailRetrieveView.as_view(),
        name='offerdetail-detail',
    ),
]
