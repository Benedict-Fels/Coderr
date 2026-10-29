from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """Everyone logged in may read, only the owner may edit."""

    def has_object_permission(self, request, view, profile):
        if request.method in SAFE_METHODS:
            return True
        return profile.user_id == request.user.id
