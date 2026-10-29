from django.contrib.auth.models import User
from rest_framework import serializers
from profile_app.models import Profile


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Diese E-Mail wird bereits verwendet.')
        return value

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Die Passwörter stimmen nicht überein.'})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')

        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, type=user_type)
        return user


class LoginSerializer(serializers.Serializer):
    """Check email and password and return the matching user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Find the user by email and check the password."""
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Invalid email or password.")

        data["user"] = user
        return data
