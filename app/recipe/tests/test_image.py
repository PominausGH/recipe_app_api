import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe


def image_upload_url(recipe_id):
    """Return URL for recipe image upload."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_test_image(width=100, height=100, format='JPEG'):
    """Create a test image file."""
    image = Image.new('RGB', (width, height), color='red')
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    image.save(tmp_file, format=format)
    tmp_file.seek(0)
    return tmp_file


class RecipeImageUploadTests(TestCase):
    """Tests for recipe image upload."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            instructions='Test instructions',
            is_published=True,
        )

    def tearDown(self):
        """Clean up test images."""
        if self.recipe.image:
            self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (500, 500), color='red')
            img.save(image_file, format='JPEG')
            image_file.seek(0)

            res = self.client.post(
                url,
                {'image': image_file},
                format='multipart',
            )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_resizes_large_image(self):
        """Test that large images are resized."""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (2000, 1500), color='blue')
            img.save(image_file, format='JPEG')
            image_file.seek(0)

            res = self.client.post(
                url,
                {'image': image_file},
                format='multipart',
            )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()

        # Check image was resized
        with Image.open(self.recipe.image.path) as img:
            self.assertLessEqual(img.width, 1200)

    def test_upload_image_bad_request(self):
        """Test uploading invalid image fails."""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(
            url, {'image': 'notanimage'}, format='multipart'
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_requires_auth(self):
        """Test uploading image requires authentication."""
        self.client.force_authenticate(user=None)
        url = image_upload_url(self.recipe.id)

        res = self.client.post(url, {}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_image_only_owner(self):
        """Test only recipe owner can upload image."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=other_user)
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(image_file, format='JPEG')
            image_file.seek(0)

            res = self.client.post(
                url,
                {'image': image_file},
                format='multipart',
            )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
