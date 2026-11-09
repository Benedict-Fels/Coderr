from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Read and update a single profile.

    The model fields id and date_joined are exposed as user and
    created_at to match the API documentation.
    """

    user = serializers.IntegerField(source='id', read_only=True)
    created_at = serializers.DateTimeField(
        source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]
        read_only_fields = ['username', 'type']

    def validate_email(self, value):
        """Reject an email address used by another user."""
        others = User.objects.exclude(pk=self.instance.pk)
        if others.filter(email=value).exists():
            raise serializers.ValidationError(
                'Diese E-Mail wird bereits verwendet.')
        return value


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """Profile data shown in the list of business users."""

    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """Profile data shown in the list of customers."""

    user = serializers.IntegerField(source='id', read_only=True)
    uploaded_at = serializers.DateTimeField(
        source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type',
        ]
