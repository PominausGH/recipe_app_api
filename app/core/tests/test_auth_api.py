from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

REGISTER_URL = reverse("auth:register")
LOGIN_URL = reverse("auth:login")
REFRESH_URL = reverse("auth:refresh")
ME_URL = reverse("auth:me")


class PublicAuthAPITests(TestCase):
    """Test unauthenticated auth API access."""

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Test registering a new user."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "name": "Test User",
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_register_password_mismatch(self):
        """Test registration fails with password mismatch."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "different",
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_exists(self):
        """Test registration fails for existing email."""
        get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        payload = {
            "email": "test@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_too_short(self):
        """Test registration fails with short password."""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "password_confirm": "pw",
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """Test login returns tokens."""
        get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
        }

        res = self.client.post(LOGIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        payload = {
            "email": "test@example.com",
            "password": "wrongpass",
        }

        res = self.client.post(LOGIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Test refreshing access token."""
        get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        login_res = self.client.post(
            LOGIN_URL,
            {
                "email": "test@example.com",
                "password": "testpass123",
            },
        )

        res = self.client.post(
            REFRESH_URL,
            {
                "refresh": login_res.data["refresh"],
            },
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_me_requires_auth(self):
        """Test me endpoint requires authentication."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAuthAPITests(TestCase):
    """Test authenticated auth API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
            name="Test User",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_me(self):
        """Test retrieving current user profile."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["name"], self.user.name)

    def test_update_me(self):
        """Test updating current user profile."""
        payload = {"name": "Updated Name", "bio": "My bio"}

        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated Name")
        self.assertEqual(self.user.bio, "My bio")

    def test_cannot_update_email(self):
        """Test email cannot be changed via profile update."""
        self.client.patch(ME_URL, {"email": "new@example.com"})

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@example.com")
