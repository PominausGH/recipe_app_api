from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe
from taxonomy.models import Category, Tag
from interaction.models import Rating


RECIPES_URL = reverse('recipe:recipe-list')


class RecipeFilterTests(TestCase):
    """Tests for recipe filtering."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

        # Create categories
        self.breakfast = Category.objects.create(
            name='Breakfast', slug='breakfast'
        )
        self.dinner = Category.objects.create(name='Dinner', slug='dinner')

        # Create tags
        self.vegan = Tag.objects.create(name='Vegan', slug='vegan')
        self.quick = Tag.objects.create(name='Quick', slug='quick')

        # Create recipes
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title='Pancakes',
            description='Fluffy pancakes',
            instructions='Mix and cook',
            category=self.breakfast,
            difficulty='easy',
            prep_time=10,
            cook_time=15,
            is_published=True,
        )
        self.recipe1.tags.add(self.quick)

        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title='Vegan Stir Fry',
            description='Healthy dinner',
            instructions='Stir fry vegetables',
            category=self.dinner,
            difficulty='medium',
            prep_time=20,
            cook_time=30,
            is_published=True,
        )
        self.recipe2.tags.add(self.vegan, self.quick)

        self.recipe3 = Recipe.objects.create(
            author=self.user,
            title='Beef Wellington',
            description='Fancy dinner',
            instructions='Complex preparation',
            category=self.dinner,
            difficulty='hard',
            prep_time=60,
            cook_time=120,
            is_published=True,
        )

    def test_filter_by_category(self):
        """Test filtering recipes by category."""
        res = self.client.get(RECIPES_URL, {'category': self.dinner.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags."""
        res = self.client.get(RECIPES_URL, {'tags': self.vegan.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], 'Vegan Stir Fry')

    def test_filter_by_multiple_tags(self):
        """Test filtering by multiple tags."""
        tag_ids = f'{self.vegan.id},{self.quick.id}'
        res = self.client.get(RECIPES_URL, {'tags': tag_ids})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Should return recipes that have ANY of the tags
        self.assertEqual(len(res.data['results']), 2)

    def test_filter_by_difficulty(self):
        """Test filtering recipes by difficulty."""
        res = self.client.get(RECIPES_URL, {'difficulty': 'easy'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], 'Pancakes')

    def test_filter_by_max_time(self):
        """Test filtering recipes by maximum total time."""
        res = self.client.get(RECIPES_URL, {'max_time': 60})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        titles = [r['title'] for r in res.data['results']]
        self.assertIn('Pancakes', titles)
        self.assertIn('Vegan Stir Fry', titles)


class RecipeSearchTests(TestCase):
    """Tests for recipe search."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

        Recipe.objects.create(
            author=self.user,
            title='Chocolate Cake',
            description='Rich chocolate dessert',
            instructions='Bake',
            is_published=True,
        )
        Recipe.objects.create(
            author=self.user,
            title='Vanilla Cupcakes',
            description='Light and fluffy',
            instructions='Mix and bake',
            is_published=True,
        )
        Recipe.objects.create(
            author=self.user,
            title='Grilled Chicken',
            description='Healthy protein',
            instructions='Grill',
            is_published=True,
        )

    def test_search_by_title(self):
        """Test searching recipes by title."""
        res = self.client.get(RECIPES_URL, {'search': 'chocolate'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], 'Chocolate Cake')

    def test_search_by_description(self):
        """Test searching recipes by description."""
        res = self.client.get(RECIPES_URL, {'search': 'fluffy'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['title'], 'Vanilla Cupcakes')

    def test_search_case_insensitive(self):
        """Test search is case insensitive."""
        res = self.client.get(RECIPES_URL, {'search': 'CHOCOLATE'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)


class RecipeOrderingTests(TestCase):
    """Tests for recipe ordering."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )

        self.recipe1 = Recipe.objects.create(
            author=self.user,
            title='Recipe A',
            instructions='Test',
            is_published=True,
        )
        self.recipe2 = Recipe.objects.create(
            author=self.user,
            title='Recipe B',
            instructions='Test',
            is_published=True,
        )

        # Add ratings
        Rating.objects.create(user=self.user, recipe=self.recipe1, score=3)
        Rating.objects.create(user=self.user2, recipe=self.recipe1, score=5)
        Rating.objects.create(user=self.user, recipe=self.recipe2, score=5)

    def test_order_by_created_desc(self):
        """Test ordering by created date descending (default)."""
        res = self.client.get(RECIPES_URL, {'ordering': '-created_at'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'][0]['title'], 'Recipe B')

    def test_order_by_created_asc(self):
        """Test ordering by created date ascending."""
        res = self.client.get(RECIPES_URL, {'ordering': 'created_at'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'][0]['title'], 'Recipe A')
