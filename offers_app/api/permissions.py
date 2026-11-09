from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessOrReadOnly(BasePermission):
    """Everyone may read, only authenticated business users may create."""

    def has_permission(self, request, view):
        """Allow safe methods for all, everything else only for business users."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.type == 'business'
