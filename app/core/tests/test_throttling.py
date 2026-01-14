from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

RECIPES_URL = reverse("recipe:recipe-list")
LOGIN_URL = reverse("auth:login")
REGISTER_URL = reverse("auth:register")
REFRESH_URL = reverse("auth:refresh")


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


class AuthThrottleConfigTests(TestCase):
    """Tests for auth endpoint throttle configuration."""

    def test_auth_throttle_rate_configured(self):
        """Test that auth throttle rate is configured in settings."""
        rates = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
        self.assertIn("auth", rates)
        # Auth rate should be defined (value varies by environment)
        self.assertIsNotNone(rates["auth"])


class LoginThrottleTests(TestCase):
    """Tests for login endpoint throttling."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="throttle@example.com",
            password="testpass123",
        )

    def test_login_view_has_auth_throttle(self):
        """Test that login view uses auth throttle class."""
        from core.views import CustomTokenObtainPairView

        throttle_classes = CustomTokenObtainPairView.throttle_classes
        throttle_names = [t.__name__ for t in throttle_classes]
        self.assertIn("AuthRateThrottle", throttle_names)

    @override_settings(
        REST_FRAMEWORK={
            **settings.REST_FRAMEWORK,
            "DEFAULT_THROTTLE_RATES": {
                **settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
                "auth": "2/minute",
            },
        }
    )
    def test_login_throttle_limits_requests(self):
        """Test that login endpoint is throttled after limit exceeded."""
        from core.throttles import AuthRateThrottle

        # Clear throttle cache to pick up new rate and clear history
        AuthRateThrottle.THROTTLE_RATES = settings.REST_FRAMEWORK[
            "DEFAULT_THROTTLE_RATES"
        ]
        cache.clear()

        payload = {"email": "throttle@example.com", "password": "wrongpass"}

        # First two requests should work (return 401 for wrong password)
        for _ in range(2):
            res = self.client.post(LOGIN_URL, payload)
            self.assertIn(
                res.status_code,
                [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK],
            )

        # Third request should be throttled
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class RegisterThrottleTests(TestCase):
    """Tests for registration endpoint throttling."""

    def setUp(self):
        self.client = APIClient()

    def test_register_view_has_auth_throttle(self):
        """Test that register view uses auth throttle class."""
        from core.views import RegisterView

        throttle_classes = RegisterView.throttle_classes
        throttle_names = [t.__name__ for t in throttle_classes]
        self.assertIn("AuthRateThrottle", throttle_names)

    @override_settings(
        REST_FRAMEWORK={
            **settings.REST_FRAMEWORK,
            "DEFAULT_THROTTLE_RATES": {
                **settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
                "auth": "2/minute",
            },
        }
    )
    def test_register_throttle_limits_requests(self):
        """Test that register endpoint is throttled after limit exceeded."""
        from core.throttles import AuthRateThrottle

        # Clear throttle cache to pick up new rate and clear history
        AuthRateThrottle.THROTTLE_RATES = settings.REST_FRAMEWORK[
            "DEFAULT_THROTTLE_RATES"
        ]
        cache.clear()

        # Make requests with different emails to avoid uniqueness constraint
        for i in range(2):
            payload = {
                "email": f"test{i}@example.com",
                "password": "testpass123",
                "password_confirm": "testpass123",
                "name": f"Test User {i}",
            }
            res = self.client.post(REGISTER_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Third request should be throttled
        payload = {
            "email": "test3@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "name": "Test User 3",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class RefreshThrottleTests(TestCase):
    """Tests for token refresh endpoint throttling."""

    def setUp(self):
        self.client = APIClient()

    def test_refresh_view_has_auth_throttle(self):
        """Test that refresh view uses auth throttle class."""
        from core.views import CustomTokenRefreshView

        throttle_classes = CustomTokenRefreshView.throttle_classes
        throttle_names = [t.__name__ for t in throttle_classes]
        self.assertIn("AuthRateThrottle", throttle_names)
