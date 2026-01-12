import tempfile
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


ME_URL = reverse('auth:me')


class ProfilePhotoUploadTests(TestCase):
    """Tests for profile photo upload."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up test images."""
        if self.user.profile_photo:
            self.user.profile_photo.delete()

    def test_upload_profile_photo(self):
        """Test uploading a profile photo."""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (500, 500), color='red')
            img.save(image_file, format='JPEG')
            image_file.seek(0)

            res = self.client.patch(
                ME_URL,
                {'profile_photo': image_file},
                format='multipart',
            )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIn('profile_photo', res.data)

    def test_profile_photo_in_response(self):
        """Test profile photo URL is in me response."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('profile_photo', res.data)
