from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'password_confirm', 'name']

    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.',
            })
        return attrs

    def create(self, validated_data):
        """Create user with encrypted password."""
        validated_data.pop('password_confirm')
        return get_user_model().objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name', 'bio', 'profile_photo', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer for public user info (for recipe author display)."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']
