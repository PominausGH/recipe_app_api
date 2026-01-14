"""Tests for health check endpoint."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
    """Tests for the health check endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_health_check_url_exists(self):
        """Test that health check URL is configured."""
        url = reverse("health-check")
        self.assertIsNotNone(url)

    def test_health_check_returns_200(self):
        """Test health check endpoint returns 200 OK."""
        url = reverse("health-check")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_health_check_returns_status_healthy(self):
        """Test health check returns healthy status."""
        url = reverse("health-check")
        res = self.client.get(url)
        self.assertEqual(res.data["status"], "healthy")

    def test_health_check_includes_database_status(self):
        """Test health check includes database connectivity status."""
        url = reverse("health-check")
        res = self.client.get(url)
        self.assertIn("database", res.data)
        self.assertEqual(res.data["database"], "connected")

    def test_health_check_accessible_without_auth(self):
        """Test health check is accessible without authentication."""
        # No authentication set up
        url = reverse("health-check")
        res = self.client.get(url)
        # Should not return 401 or 403
        self.assertNotIn(
            res.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
