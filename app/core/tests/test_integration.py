from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


class AuthFlowIntegrationTests(TestCase):
    """Integration tests for authentication flow."""

    def setUp(self):
        self.client = APIClient()

    def test_full_registration_login_flow(self):
        """Test complete registration and login flow."""
        # Step 1: Register a new user
        register_url = reverse("auth:register")
        register_payload = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "name": "New User",
        }

        res = self.client.post(register_url, register_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("email", res.data)
        self.assertNotIn("password", res.data)

        # Verify user was created in database
        user = get_user_model().objects.get(email="newuser@example.com")
        self.assertEqual(user.name, "New User")
        self.assertTrue(user.check_password("securepass123"))

        # Step 2: Login with the new user
        login_url = reverse("auth:login")
        login_payload = {
            "email": "newuser@example.com",
            "password": "securepass123",
        }

        res = self.client.post(login_url, login_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        access_token = res.data["access"]
        refresh_token = res.data["refresh"]

        # Step 3: Access protected endpoint with token
        me_url = reverse("auth:me")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "newuser@example.com")
        self.assertEqual(res.data["name"], "New User")

        # Step 4: Update profile
        res = self.client.patch(me_url, {"bio": "I love cooking!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["bio"], "I love cooking!")

        # Step 5: Refresh token
        refresh_url = reverse("auth:refresh")
        self.client.credentials()  # Clear auth

        res = self.client.post(refresh_url, {"refresh": refresh_token})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

        # Step 6: Use new access token
        new_access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")

        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        me_url = reverse("auth:me")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken123")

        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_token_can_be_refreshed(self):
        """Test token refresh workflow."""
        # Create and login user
        get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

        login_url = reverse("auth:login")
        res = self.client.post(
            login_url,
            {
                "email": "test@example.com",
                "password": "testpass123",
            },
        )

        refresh_token = res.data["refresh"]

        # Use refresh token to get new access token
        refresh_url = reverse("auth:refresh")
        res = self.client.post(refresh_url, {"refresh": refresh_token})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
