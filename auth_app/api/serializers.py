from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a new user."""

    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=User.TYPE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'repeated_password', 'type',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        """Reject an email address that is already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Diese E-Mail wird bereits verwendet.')
        return value

    def validate(self, data):
        """Check that both passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Die Passwörter stimmen nicht überein.'})
        return data

    def create(self, validated_data):
        """Create the user with a hashed password."""
        validated_data.pop('repeated_password')
        return User.objects.create_user(**validated_data)
