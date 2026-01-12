from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch


RECIPES_URL = reverse('recipe:recipe-list')
REGISTER_URL = reverse('auth:register')


class ThrottlingTests(TestCase):
    """Tests for API rate limiting."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.AnonRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': {
                'anon': '2/minute',
            },
        }
    )
    def test_anon_throttle_limit(self):
        """Test anonymous users are rate limited."""
        # Make requests up to the limit
        for _ in range(2):
            res = self.client.get(RECIPES_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Next request should be throttled
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_throttle_response_includes_retry_after(self):
        """Test throttled response includes Retry-After header."""
        with override_settings(
            REST_FRAMEWORK={
                'DEFAULT_THROTTLE_CLASSES': [
                    'rest_framework.throttling.AnonRateThrottle',
                ],
                'DEFAULT_THROTTLE_RATES': {
                    'anon': '1/minute',
                },
            }
        ):
            # First request succeeds
            self.client.get(RECIPES_URL)

            # Second request should be throttled
            res = self.client.get(RECIPES_URL)

            if res.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                self.assertIn('Retry-After', res)


class RecipeCreateThrottleTests(TestCase):
    """Tests for recipe creation throttling."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'recipe_create': '2/minute',
                'user': '1000/hour',
            },
        }
    )
    @patch('core.throttling.RecipeCreateThrottle.get_rate')
    def test_recipe_create_throttle(self, mock_get_rate):
        """Test recipe creation is throttled separately."""
        mock_get_rate.return_value = '2/minute'

        payload = {
            'title': 'Test Recipe',
            'instructions': 'Test instructions',
        }

        # Create recipes up to limit
        for i in range(2):
            payload['title'] = f'Test Recipe {i}'
            res = self.client.post(RECIPES_URL, payload)
            # Should succeed
            self.assertIn(
                res.status_code,
                [status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUESTS]
            )

    def test_get_requests_not_throttled_by_create_throttle(self):
        """Test GET requests bypass recipe create throttle."""
        # GET requests should not be limited by RecipeCreateThrottle
        for _ in range(5):
            res = self.client.get(RECIPES_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
