from core.models import EmailVerificationToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "password_confirm", "name"]

    def validate(self, attrs):
        """Validate passwords match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": "Passwords do not match.",
                }
            )
        return attrs

    def create(self, validated_data):
        """Create user with encrypted password and send verification email."""
        validated_data.pop("password_confirm")
        user = get_user_model().objects.create_user(**validated_data)

        # Create verification token and send email
        token = EmailVerificationToken.objects.create(user=user)
        self._send_verification_email(user, token)

        return user

    def _send_verification_email(self, user, token):
        """Send verification email to user."""
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        verification_url = f"{frontend_url}/verify-email?token={token.token}"

        subject = "Verify your Recipe App account"
        message = f"""Hi {user.name or "there"},

Welcome to Recipe App! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, you can safely ignore this email.

Thanks,
The Recipe App Team
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "name", "bio", "profile_photo", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer for public user info (for recipe author display)."""

    class Meta:
        model = get_user_model()
        fields = ["id", "name"]
        read_only_fields = ["id", "name"]
