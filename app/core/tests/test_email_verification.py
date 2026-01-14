"""Tests for email verification functionality."""

from datetime import timedelta

from core.models import EmailVerificationToken
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient


class EmailVerificationModelTests(TestCase):
    """Tests for email verification models."""

    def test_user_has_is_email_verified_field(self):
        """Test that User model has is_email_verified field."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.assertFalse(user.is_email_verified)

    def test_user_is_email_verified_defaults_to_false(self):
        """Test that is_email_verified defaults to False."""
        user = get_user_model().objects.create_user(
            email="test2@example.com",
            password="testpass123",
        )
        self.assertFalse(user.is_email_verified)

    def test_create_email_verification_token(self):
        """Test creating an email verification token."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        token = EmailVerificationToken.objects.create(user=user)

        self.assertIsNotNone(token.token)
        self.assertEqual(token.user, user)
        self.assertIsNotNone(token.created_at)
        self.assertIsNotNone(token.expires_at)

    def test_email_verification_token_expires_in_24_hours(self):
        """Test that token expires approximately 24 hours from creation."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        token = EmailVerificationToken.objects.create(user=user)

        # Check expires_at is approximately 24 hours from now
        expected_expiry = timezone.now() + timedelta(hours=24)
        time_diff = abs((token.expires_at - expected_expiry).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute

    def test_email_verification_token_is_expired(self):
        """Test is_expired method on token."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        token = EmailVerificationToken.objects.create(user=user)

        # Fresh token should not be expired
        self.assertFalse(token.is_expired)

        # Manually set expires_at to past
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        self.assertTrue(token.is_expired)

    def test_email_verification_token_str(self):
        """Test token string representation."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        token = EmailVerificationToken.objects.create(user=user)

        self.assertIn("test@example.com", str(token))


VERIFY_EMAIL_URL = reverse("auth:verify-email")


class VerifyEmailAPITests(TestCase):
    """Tests for the verify-email endpoint."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.token = EmailVerificationToken.objects.create(user=self.user)

    def test_verify_email_with_valid_token(self):
        """Test verifying email with valid token."""
        payload = {"token": self.token.token}
        res = self.client.post(VERIFY_EMAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh user from database
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_email_deletes_token_after_use(self):
        """Test that token is deleted after successful verification."""
        payload = {"token": self.token.token}
        self.client.post(VERIFY_EMAIL_URL, payload)

        # Token should be deleted
        self.assertFalse(
            EmailVerificationToken.objects.filter(token=self.token.token).exists()
        )

    def test_verify_email_with_invalid_token(self):
        """Test verifying email with invalid token fails."""
        payload = {"token": "invalid-token"}
        res = self.client.post(VERIFY_EMAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_with_expired_token(self):
        """Test verifying email with expired token fails."""
        # Set token to expired
        self.token.expires_at = timezone.now() - timedelta(hours=1)
        self.token.save()

        payload = {"token": self.token.token}
        res = self.client.post(VERIFY_EMAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired", res.data.get("error", "").lower())

    def test_verify_email_without_token(self):
        """Test verifying email without token fails."""
        res = self.client.post(VERIFY_EMAIL_URL, {})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


RESEND_VERIFICATION_URL = reverse("auth:resend-verification")


class ResendVerificationAPITests(TestCase):
    """Tests for the resend-verification endpoint."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_resend_verification_creates_new_token(self):
        """Test resending verification creates a new token."""
        payload = {"email": self.user.email}
        res = self.client.post(RESEND_VERIFICATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(EmailVerificationToken.objects.filter(user=self.user).exists())

    def test_resend_verification_deletes_old_tokens(self):
        """Test resending verification deletes old tokens."""
        # Create an existing token
        old_token = EmailVerificationToken.objects.create(user=self.user)
        old_token_value = old_token.token

        payload = {"email": self.user.email}
        self.client.post(RESEND_VERIFICATION_URL, payload)

        # Old token should be deleted
        self.assertFalse(
            EmailVerificationToken.objects.filter(token=old_token_value).exists()
        )
        # New token should exist
        self.assertTrue(EmailVerificationToken.objects.filter(user=self.user).exists())

    def test_resend_verification_for_already_verified_user(self):
        """Test resending verification for already verified user fails."""
        self.user.is_email_verified = True
        self.user.save()

        payload = {"email": self.user.email}
        res = self.client.post(RESEND_VERIFICATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already verified", res.data.get("error", "").lower())

    def test_resend_verification_for_nonexistent_email(self):
        """Test resending verification for nonexistent email returns success."""
        # Should return success to prevent email enumeration
        payload = {"email": "nonexistent@example.com"}
        res = self.client.post(RESEND_VERIFICATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_resend_verification_without_email(self):
        """Test resending verification without email fails."""
        res = self.client.post(RESEND_VERIFICATION_URL, {})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
