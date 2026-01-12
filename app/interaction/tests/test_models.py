from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from recipe.models import Recipe
from interaction.models import Rating, Favorite


class RatingModelTests(TestCase):
    """Tests for Rating model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            instructions='Test instructions',
            is_published=True,
        )

    def test_create_rating(self):
        """Test creating a rating is successful."""
        rating = Rating.objects.create(
            user=self.user,
            recipe=self.recipe,
            score=5,
            review='Great recipe!',
        )

        self.assertEqual(rating.score, 5)
        self.assertEqual(rating.review, 'Great recipe!')
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.recipe, self.recipe)

    def test_rating_score_range(self):
        """Test rating score must be 1-5."""
        rating = Rating(
            user=self.user,
            recipe=self.recipe,
            score=6,
        )
        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_rating_unique_user_recipe(self):
        """Test user can only rate a recipe once."""
        Rating.objects.create(
            user=self.user,
            recipe=self.recipe,
            score=4,
        )

        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                user=self.user,
                recipe=self.recipe,
                score=5,
            )

    def test_rating_str(self):
        """Test rating string representation."""
        rating = Rating.objects.create(
            user=self.user,
            recipe=self.recipe,
            score=4,
        )
        expected = f'{self.user.email} rated {self.recipe.title}: 4'
        self.assertEqual(str(rating), expected)


class FavoriteModelTests(TestCase):
    """Tests for Favorite model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            instructions='Test instructions',
            is_published=True,
        )

    def test_create_favorite(self):
        """Test creating a favorite is successful."""
        favorite = Favorite.objects.create(
            user=self.user,
            recipe=self.recipe,
        )

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.recipe, self.recipe)
        self.assertIsNotNone(favorite.created_at)

    def test_favorite_unique_user_recipe(self):
        """Test user can only favorite a recipe once."""
        Favorite.objects.create(
            user=self.user,
            recipe=self.recipe,
        )

        with self.assertRaises(IntegrityError):
            Favorite.objects.create(
                user=self.user,
                recipe=self.recipe,
            )

    def test_favorite_str(self):
        """Test favorite string representation."""
        favorite = Favorite.objects.create(
            user=self.user,
            recipe=self.recipe,
        )
        expected = f'{self.user.email} favorited {self.recipe.title}'
        self.assertEqual(str(favorite), expected)
