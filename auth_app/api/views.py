from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer


def build_auth_response(user):
    """Return the token and basic user data for the given user."""
    token, created = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'username': user.username,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(APIView):
    """Register a new customer or business user."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create the user and return its token."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            build_auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    """Log in with username and password."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Check the credentials and return the user's token."""
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(
            build_auth_response(user), status=status.HTTP_200_OK)
