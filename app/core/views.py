from core.serializers import UserProfileSerializer, UserRegistrationSerializer
from core.throttles import AuthRateThrottle
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
