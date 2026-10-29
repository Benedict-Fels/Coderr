from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """Everyone logged in may read, only the owner may edit."""

    def has_object_permission(self, request, view, user):
        if request.method in SAFE_METHODS:
            return True
        # Profil und User sind jetzt dasselbe Objekt -> direkt vergleichen
        return user == request.user
