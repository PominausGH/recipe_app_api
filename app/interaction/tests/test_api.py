from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe
from interaction.models import Rating, Favorite, Comment


def rate_url(recipe_id):
    """Return recipe rate URL."""
    return reverse('recipe:recipe-rate', args=[recipe_id])


def favorite_url(recipe_id):
    """Return recipe favorite URL."""
    return reverse('recipe:recipe-favorite', args=[recipe_id])


def comments_url(recipe_id):
    """Return recipe comments URL."""
    return reverse('recipe:recipe-comments', args=[recipe_id])


class RatingAPITests(TestCase):
    """Tests for rating API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
        )
        self.recipe = Recipe.objects.create(
            author=self.other_user,
            title='Test Recipe',
            instructions='Test instructions',
            is_published=True,
        )

    def test_rate_recipe_requires_auth(self):
        """Test rating requires authentication."""
        res = self.client.post(rate_url(self.recipe.id), {'score': 5})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_recipe(self):
        """Test rating a recipe."""
        self.client.force_authenticate(user=self.user)
        payload = {'score': 5, 'review': 'Excellent!'}

        res = self.client.post(rate_url(self.recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Rating.objects.filter(
            user=self.user,
            recipe=self.recipe,
        ).exists())

    def test_update_existing_rating(self):
        """Test updating an existing rating."""
        self.client.force_authenticate(user=self.user)
        Rating.objects.create(user=self.user, recipe=self.recipe, score=3)

        res = self.client.post(rate_url(self.recipe.id), {'score': 5})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        rating = Rating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.score, 5)

    def test_invalid_rating_score(self):
        """Test rating with invalid score."""
        self.client.force_authenticate(user=self.user)

        res = self.client.post(rate_url(self.recipe.id), {'score': 6})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class FavoriteAPITests(TestCase):
    """Tests for favorite API."""

    def setUp(self):
        self.client = APIClient()
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

    def test_favorite_requires_auth(self):
        """Test favoriting requires authentication."""
        res = self.client.post(favorite_url(self.recipe.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_favorite(self):
        """Test adding a recipe to favorites."""
        self.client.force_authenticate(user=self.user)

        res = self.client.post(favorite_url(self.recipe.id))

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(
            user=self.user,
            recipe=self.recipe,
        ).exists())

    def test_remove_favorite(self):
        """Test removing a recipe from favorites (toggle)."""
        self.client.force_authenticate(user=self.user)
        Favorite.objects.create(user=self.user, recipe=self.recipe)

        res = self.client.post(favorite_url(self.recipe.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Favorite.objects.filter(
            user=self.user,
            recipe=self.recipe,
        ).exists())


class CommentAPITests(TestCase):
    """Tests for comment API."""

    def setUp(self):
        self.client = APIClient()
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

    def test_list_comments(self):
        """Test listing comments on a recipe."""
        Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='Great recipe!',
        )

        res = self.client.get(comments_url(self.recipe.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_comment_requires_auth(self):
        """Test creating comment requires authentication."""
        res = self.client.post(comments_url(self.recipe.id), {'text': 'Test'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment(self):
        """Test creating a comment."""
        self.client.force_authenticate(user=self.user)

        res = self.client.post(comments_url(self.recipe.id), {'text': 'Nice!'})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_reply(self):
        """Test creating a reply to a comment."""
        self.client.force_authenticate(user=self.user)
        parent = Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='Original comment',
        )

        res = self.client.post(
            comments_url(self.recipe.id),
            {'text': 'Reply', 'parent': parent.id},
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        reply = Comment.objects.get(id=res.data['id'])
        self.assertEqual(reply.parent, parent)
