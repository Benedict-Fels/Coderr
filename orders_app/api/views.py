from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .permissions import IsCustomerOrReadOnly, IsOrderBusinessUser
from .serializers import OrderCreateSerializer, OrderSerializer

User = get_user_model()


class OrderListCreateView(generics.ListCreateAPIView):
    """List the user's orders and let customers create new ones."""

    permission_classes = [IsAuthenticated, IsCustomerOrReadOnly]

    def get_queryset(self):
        """Return orders where the user is customer or business user."""
        user = self.request.user
        customer_orders = Order.objects.filter(customer_user=user)
        business_orders = Order.objects.filter(business_user=user)
        return customer_orders | business_orders

    def get_serializer_class(self):
        """Use the create serializer for POST, the full one otherwise."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """Save the logged-in user as customer."""
        serializer.save(customer_user=self.request.user)


class OrderUpdateDestroyView(generics.UpdateAPIView,
                             generics.DestroyAPIView):
    """Let the business user update the status, let admins delete."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['patch', 'delete']

    def get_permissions(self):
        """Admins may delete, the order's business user may update."""
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated(), IsOrderBusinessUser()]


class BaseOrderCountView(APIView):
    """Count the orders of a business user with a given status."""

    status = None
    response_key = None

    def get(self, request, business_user_id):
        """Return the number of matching orders, 404 for non-business."""
        business_user = get_object_or_404(
            User, id=business_user_id, type='business')
        count = business_user.business_orders.filter(
            status=self.status).count()
        return Response({self.response_key: count})


class OrderCountView(BaseOrderCountView):
    """Number of orders in progress of a business user."""

    status = 'in_progress'
    response_key = 'order_count'


class CompletedOrderCountView(BaseOrderCountView):
    """Number of completed orders of a business user."""

    status = 'completed'
    response_key = 'completed_order_count'
