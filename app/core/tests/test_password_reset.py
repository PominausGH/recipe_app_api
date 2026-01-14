"""Tests for password reset functionality."""

from datetime import timedelta

from core.models import PasswordResetToken
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient


def create_user(**params):
    """Create and return a test user."""
    defaults = {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class PasswordResetTokenModelTests(TestCase):
    """Test password reset token model."""

    def test_create_token_generates_unique_token(self):
        """Test that creating a token generates a unique token string."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)

        self.assertIsNotNone(token.token)
        self.assertTrue(len(token.token) > 20)

    def test_token_expires_after_one_hour(self):
        """Test that token expires after 1 hour."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)

        # Token should not be expired initially
        self.assertFalse(token.is_expired)

        # Manually set expires_at to past
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()

        self.assertTrue(token.is_expired)

    def test_token_default_expiration_is_one_hour(self):
        """Test that default expiration is 1 hour from creation."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)

        # Expiration should be approximately 1 hour from now
        expected_expiry = timezone.now() + timedelta(hours=1)
        delta = abs((token.expires_at - expected_expiry).total_seconds())
        self.assertLess(delta, 5)  # Within 5 seconds


class PasswordResetRequestAPITests(TestCase):
    """Tests for POST /api/auth/password-reset/."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("auth:password-reset")

    def test_request_reset_with_valid_email(self):
        """Test requesting password reset with valid email."""
        user = create_user(email="user@example.com")

        res = self.client.post(self.url, {"email": "user@example.com"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("message", res.data)
        # Should create a token
        self.assertTrue(PasswordResetToken.objects.filter(user=user).exists())

    def test_request_reset_sends_email(self):
        """Test that requesting reset sends an email."""
        create_user(email="user@example.com")

        res = self.client.post(self.url, {"email": "user@example.com"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("password", mail.outbox[0].subject.lower())

    def test_request_reset_with_nonexistent_email_returns_success(self):
        """Test that non-existent email returns success (prevent enumeration)."""
        res = self.client.post(self.url, {"email": "nonexistent@example.com"})

        # Should return success to prevent email enumeration
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("message", res.data)

    def test_request_reset_without_email_returns_error(self):
        """Test that missing email returns error."""
        res = self.client.post(self.url, {})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_reset_deletes_old_tokens(self):
        """Test that requesting new reset deletes old tokens."""
        user = create_user(email="user@example.com")
        old_token = PasswordResetToken.objects.create(user=user)
        old_token_value = old_token.token

        self.client.post(self.url, {"email": "user@example.com"})

        # Old token should be deleted
        self.assertFalse(
            PasswordResetToken.objects.filter(token=old_token_value).exists()
        )
        # New token should exist
        self.assertEqual(PasswordResetToken.objects.filter(user=user).count(), 1)


class PasswordResetConfirmAPITests(TestCase):
    """Tests for POST /api/auth/password-reset-confirm/."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("auth:password-reset-confirm")

    def test_reset_password_with_valid_token(self):
        """Test resetting password with valid token."""
        user = create_user(email="user@example.com", password="oldpassword123")
        token = PasswordResetToken.objects.create(user=user)

        res = self.client.post(
            self.url,
            {
                "token": token.token,
                "password": "newpassword123",
                "password_confirm": "newpassword123",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # User should be able to login with new password
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpassword123"))

    def test_reset_password_deletes_token(self):
        """Test that successful reset deletes the token."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)
        token_value = token.token

        self.client.post(
            self.url,
            {
                "token": token_value,
                "password": "newpassword123",
                "password_confirm": "newpassword123",
            },
        )

        self.assertFalse(PasswordResetToken.objects.filter(token=token_value).exists())

    def test_reset_password_with_expired_token_returns_error(self):
        """Test that expired token returns error."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()

        res = self.client.post(
            self.url,
            {
                "token": token.token,
                "password": "newpassword123",
                "password_confirm": "newpassword123",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired", res.data.get("error", "").lower())

    def test_reset_password_with_invalid_token_returns_error(self):
        """Test that invalid token returns error."""
        res = self.client.post(
            self.url,
            {
                "token": "invalidtoken123",
                "password": "newpassword123",
                "password_confirm": "newpassword123",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_mismatched_passwords_returns_error(self):
        """Test that mismatched passwords return error."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)

        res = self.client.post(
            self.url,
            {
                "token": token.token,
                "password": "newpassword123",
                "password_confirm": "differentpassword",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_without_token_returns_error(self):
        """Test that missing token returns error."""
        res = self.client.post(
            self.url,
            {
                "password": "newpassword123",
                "password_confirm": "newpassword123",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_weak_password_returns_error(self):
        """Test that weak password returns error."""
        user = create_user()
        token = PasswordResetToken.objects.create(user=user)

        res = self.client.post(
            self.url,
            {
                "token": token.token,
                "password": "short",
                "password_confirm": "short",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
