from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status


RECIPES_URL = reverse("recipe:recipe-list")


class ThrottlingConfigTests(TestCase):
    """Tests for API rate limiting configuration."""

    def test_throttle_settings_configured(self):
        """Test that throttle settings are properly configured."""
        rf_settings = settings.REST_FRAMEWORK

        # Check throttle classes are configured
        self.assertIn("DEFAULT_THROTTLE_CLASSES", rf_settings)
        self.assertIn(
            "rest_framework.throttling.AnonRateThrottle",
            rf_settings["DEFAULT_THROTTLE_CLASSES"],
        )
        self.assertIn(
            "rest_framework.throttling.UserRateThrottle",
            rf_settings["DEFAULT_THROTTLE_CLASSES"],
        )

        # Check throttle rates are configured
        self.assertIn("DEFAULT_THROTTLE_RATES", rf_settings)
        self.assertIn("anon", rf_settings["DEFAULT_THROTTLE_RATES"])
        self.assertIn("user", rf_settings["DEFAULT_THROTTLE_RATES"])
        self.assertIn("recipe_create", rf_settings["DEFAULT_THROTTLE_RATES"])

    def test_throttle_rates_values(self):
        """Test throttle rates have expected values."""
        rates = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]

        self.assertEqual(rates["anon"], "100/hour")
        self.assertEqual(rates["user"], "1000/hour")
        self.assertEqual(rates["recipe_create"], "20/day")


class RecipeCreateThrottleTests(TestCase):
    """Tests for recipe creation throttling behavior."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_requests_not_throttled_by_create_throttle(self):
        """Test GET requests bypass recipe create throttle."""
        # GET requests should not be limited by RecipeCreateThrottle
        for _ in range(5):
            res = self.client.get(RECIPES_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_create_recipe(self):
        """Test authenticated user can create a recipe."""
        payload = {
            "title": "Test Recipe",
            "instructions": "Test instructions",
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
