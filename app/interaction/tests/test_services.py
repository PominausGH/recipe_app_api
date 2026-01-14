from django.contrib.auth import get_user_model
from django.test import TestCase
from interaction.models import Favorite, FeedPreference, Follow, Mute, Rating
from interaction.services.feed import FeedService
from recipe.models import Recipe


class FeedServiceTests(TestCase):
    """Tests for feed generation service."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123",
        )
        self.followed_user = get_user_model().objects.create_user(
            email="followed@example.com",
            password="testpass123",
        )
        Follow.objects.create(follower=self.user, following=self.followed_user)

    def test_feed_includes_followed_user_recipes(self):
        """Test feed includes recipes from followed users."""
        recipe = Recipe.objects.create(
            author=self.followed_user,
            title="Test Recipe",
            instructions="Test",
            is_published=True,
        )
        feed = FeedService.get_feed(self.user)

        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0]["type"], "recipe")
        self.assertEqual(feed[0]["recipe"].id, recipe.id)

    def test_feed_excludes_muted_users(self):
        """Test feed excludes content from muted users."""
        Recipe.objects.create(
            author=self.followed_user,
            title="Test Recipe",
            instructions="Test",
            is_published=True,
        )
        Mute.objects.create(user=self.user, muted_user=self.followed_user)

        feed = FeedService.get_feed(self.user)
        self.assertEqual(len(feed), 0)

    def test_feed_respects_preferences(self):
        """Test feed respects user preferences."""
        recipe = Recipe.objects.create(
            author=self.followed_user,
            title="Test Recipe",
            instructions="Test",
            is_published=True,
        )
        Rating.objects.create(
            user=self.followed_user,
            recipe=recipe,
            score=5,
        )
        FeedPreference.objects.create(
            user=self.user,
            show_recipes=True,
            show_ratings=False,
        )

        feed = FeedService.get_feed(self.user)
        types = [item["type"] for item in feed]
        self.assertIn("recipe", types)
        self.assertNotIn("rating", types)

    def test_feed_chronological_order(self):
        """Test feed is in chronological order."""
        recipe1 = Recipe.objects.create(
            author=self.followed_user,
            title="First Recipe",
            instructions="Test",
            is_published=True,
        )
        recipe2 = Recipe.objects.create(
            author=self.followed_user,
            title="Second Recipe",
            instructions="Test",
            is_published=True,
        )

        feed = FeedService.get_feed(self.user, order="chronological")
        self.assertEqual(feed[0]["recipe"].id, recipe2.id)
        self.assertEqual(feed[1]["recipe"].id, recipe1.id)

    def test_feed_includes_favorites_when_enabled(self):
        """Test feed includes favorites when preference is enabled."""
        recipe = Recipe.objects.create(
            author=self.user,  # User's own recipe
            title="Test Recipe",
            instructions="Test",
            is_published=True,
        )
        Favorite.objects.create(user=self.followed_user, recipe=recipe)
        FeedPreference.objects.create(
            user=self.user,
            show_favorites=True,
        )

        feed = FeedService.get_feed(self.user)
        types = [item["type"] for item in feed]
        self.assertIn("favorite", types)
