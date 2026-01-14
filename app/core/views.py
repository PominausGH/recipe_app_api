from core.models import EmailVerificationToken, PasswordResetToken
from core.serializers import UserProfileSerializer, UserRegistrationSerializer
from core.throttles import AuthRateThrottle
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class RegisterView(generics.CreateAPIView):
    """View for user registration."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with auth throttling."""

    throttle_classes = [AuthRateThrottle]


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view with auth throttling."""

    throttle_classes = [AuthRateThrottle]


class MeView(generics.RetrieveUpdateAPIView):
    """View for current user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user


class LogoutView(APIView):
    """View to blacklist refresh token on logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request):
        """Return health status including database connectivity."""
        from django.db import connection

        # Check database connectivity
        db_status = "connected"
        try:
            connection.ensure_connection()
        except Exception:
            db_status = "disconnected"

        return Response(
            {
                "status": "healthy",
                "database": db_status,
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    """View to verify email address."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        """Verify email with token."""
        token_value = request.data.get("token")

        if not token_value:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = EmailVerificationToken.objects.get(token=token_value)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.is_expired:
            return Response(
                {"error": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify the user's email
        user = token.user
        user.is_email_verified = True
        user.save()

        # Delete the token
        token.delete()

        return Response(
            {"message": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class ResendVerificationView(APIView):
    """View to resend email verification."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        """Resend verification email."""
        from django.contrib.auth import get_user_model

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try to find user
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return success to prevent email enumeration
            return Response(
                {"message": "If the email exists, a verification email has been sent."},
                status=status.HTTP_200_OK,
            )

        if user.is_email_verified:
            return Response(
                {"error": "Email is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete old tokens
        EmailVerificationToken.objects.filter(user=user).delete()

        # Create new token
        token = EmailVerificationToken.objects.create(user=user)

        # Send verification email
        self._send_verification_email(user, token)

        return Response(
            {"message": "If the email exists, a verification email has been sent."},
            status=status.HTTP_200_OK,
        )

    def _send_verification_email(self, user, token):
        """Send verification email to user."""
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        verification_url = f"{frontend_url}/verify-email?token={token.token}"

        subject = "Verify your Recipe App account"
        message = f"""Hi {user.name or "there"},

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't request this, you can safely ignore this email.

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


class PasswordResetRequestView(APIView):
    """View to request password reset."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        """Request password reset email."""
        from django.contrib.auth import get_user_model

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try to find user
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return success to prevent email enumeration
            return Response(
                {"message": "If an account exists, a reset link has been sent."},
                status=status.HTTP_200_OK,
            )

        # Delete old tokens
        PasswordResetToken.objects.filter(user=user).delete()

        # Create new token
        token = PasswordResetToken.objects.create(user=user)

        # Send reset email
        self._send_reset_email(user, token)

        return Response(
            {"message": "If an account exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )

    def _send_reset_email(self, user, token):
        """Send password reset email to user."""
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        reset_url = f"{frontend_url}/reset-password?token={token.token}"

        subject = "Reset your Recipe App password"
        message = f"""Hi {user.name or "there"},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

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


class PasswordResetConfirmView(APIView):
    """View to confirm password reset."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        """Reset password with token."""
        token_value = request.data.get("token")
        password = request.data.get("password")
        password_confirm = request.data.get("password_confirm")

        if not token_value:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password or not password_confirm:
            return Response(
                {"error": "Password and password confirmation are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password_confirm:
            return Response(
                {"error": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = PasswordResetToken.objects.get(token=token_value)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.is_expired:
            return Response(
                {"error": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset the password
        user = token.user
        user.set_password(password)
        user.save()

        # Delete the token
        token.delete()

        return Response(
            {"message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )
