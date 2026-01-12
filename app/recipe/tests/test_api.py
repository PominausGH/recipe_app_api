from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()

    def test_list_published_recipes(self):
        """Test listing published recipes."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
        )
        Recipe.objects.create(
            author=user,
            title='Published Recipe',
            instructions='Test',
            is_published=True,
        )
        Recipe.objects.create(
            author=user,
            title='Draft Recipe',
            instructions='Test',
            is_published=False,
        )

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_create_recipe_requires_auth(self):
        """Test creating recipe requires authentication."""
        payload = {'title': 'Test', 'instructions': 'Test'}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Test Recipe',
            'instructions': 'Test instructions',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 4,
            'difficulty': 'easy',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.author, self.user)

    def test_update_own_recipe(self):
        """Test updating own recipe."""
        recipe = Recipe.objects.create(
            author=self.user,
            title='Original',
            instructions='Test',
        )

        res = self.client.patch(detail_url(recipe.id), {'title': 'Updated'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'Updated')

    def test_cannot_update_other_users_recipe(self):
        """Test cannot update another user's recipe."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='test123',
        )
        recipe = Recipe.objects.create(
            author=other_user,
            title='Other Recipe',
            instructions='Test',
            is_published=True,
        )

        res = self.client.patch(detail_url(recipe.id), {'title': 'Hacked'})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
