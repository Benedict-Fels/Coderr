from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerOrReadOnly(BasePermission):
    """Everyone may read, only customers may create orders."""

    def has_permission(self, request, view):
        """Allow safe methods for all, POST only for customers."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == 'customer'


class IsOrderBusinessUser(BasePermission):
    """Only the business user of an order may change it."""

    def has_object_permission(self, request, view, order):
        """Check that the logged-in user is the order's business user."""
        return order.business_user == request.user
