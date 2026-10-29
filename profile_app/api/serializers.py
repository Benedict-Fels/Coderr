from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    # Model heißt id / date_joined, die Doku will user / created_at -> umbenennen per source
    user = serializers.IntegerField(source='id', read_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at',
        ]
        read_only_fields = ['username', 'type']

    def validate_email(self, value):
        # Wie bei der Registrierung: keine doppelten E-Mails (die eigene zählt nicht)
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Diese E-Mail wird bereits verwendet.')
        return value


class BusinessProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)
    uploaded_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type']
