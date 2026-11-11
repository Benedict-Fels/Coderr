from django.urls import path

from .views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderListCreateView,
    OrderUpdateDestroyView,
)

urlpatterns = [
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderUpdateDestroyView.as_view()),
    path(
        'order-count/<int:business_user_id>/',
        OrderCountView.as_view(),
    ),
    path(
        'completed-order-count/<int:business_user_id>/',
        CompletedOrderCountView.as_view(),
    ),
]
