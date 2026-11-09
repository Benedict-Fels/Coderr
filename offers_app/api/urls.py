from django.urls import path

from .views import OfferDetailRetrieveView, OfferListCreateView

urlpatterns = [
    path('offers/', OfferListCreateView.as_view()),
    path(
        'offerdetails/<int:pk>/',
        OfferDetailRetrieveView.as_view(),
        name='offerdetail-detail',
    ),
]
