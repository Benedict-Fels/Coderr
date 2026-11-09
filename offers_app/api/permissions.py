from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessOrReadOnly(BasePermission):
    """Everyone may read, only authenticated business users may create."""

    def has_permission(self, request, view):
        """Allow safe methods for all, the rest only for business users."""
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and user.type == 'business'
