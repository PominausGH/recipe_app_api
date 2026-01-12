from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe
from interaction.models import Rating, Favorite, Comment


class RecipeInteractionIntegrationTests(TestCase):
    """Integration tests for recipe interactions (ratings, favorites, comments)."""

    def setUp(self):
        self.client = APIClient()
        self.chef = get_user_model().objects.create_user(
            email='chef@example.com',
            password='testpass123',
            name='Chef User',
        )
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Regular User',
        )
        self.recipe = Recipe.objects.create(
            author=self.chef,
            title='Delicious Pasta',
            instructions='Cook pasta, add sauce',
            is_published=True,
        )

    def test_rating_and_average_calculation(self):
        """Test rating flow and average rating calculation."""
        # User 1 rates the recipe
        self.client.force_authenticate(user=self.user)
        rate_url = reverse('recipe:recipe-rate', args=[self.recipe.id])

        res = self.client.post(rate_url, {'score': 5, 'review': 'Amazing!'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Verify rating in database
        rating = Rating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.score, 5)
        self.assertEqual(rating.review, 'Amazing!')

        # User 2 rates the recipe
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=user2)
        res = self.client.post(rate_url, {'score': 3})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check average rating in recipe detail
        detail_url = reverse('recipe:recipe-detail', args=[self.recipe.id])
        res = self.client.get(detail_url)
        self.assertEqual(res.data['average_rating'], 4.0)  # (5+3)/2
        self.assertEqual(res.data['rating_count'], 2)

    def test_update_existing_rating(self):
        """Test updating an existing rating."""
        self.client.force_authenticate(user=self.user)
        rate_url = reverse('recipe:recipe-rate', args=[self.recipe.id])

        # Initial rating
        self.client.post(rate_url, {'score': 3})

        # Update rating
        res = self.client.post(rate_url, {'score': 5, 'review': 'Changed my mind!'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify only one rating exists
        self.assertEqual(Rating.objects.filter(user=self.user, recipe=self.recipe).count(), 1)
        rating = Rating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.score, 5)

    def test_favorite_toggle_flow(self):
        """Test adding and removing favorites."""
        self.client.force_authenticate(user=self.user)
        favorite_url = reverse('recipe:recipe-favorite', args=[self.recipe.id])

        # Add to favorites
        res = self.client.post(favorite_url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.user, recipe=self.recipe).exists())

        # Toggle off (remove from favorites)
        res = self.client.post(favorite_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Favorite.objects.filter(user=self.user, recipe=self.recipe).exists())

        # Toggle on again
        res = self.client.post(favorite_url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_comment_thread(self):
        """Test creating comments and replies."""
        self.client.force_authenticate(user=self.user)
        comments_url = reverse('recipe:recipe-comments', args=[self.recipe.id])

        # Create a comment
        res = self.client.post(comments_url, {'text': 'Great recipe!'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comment_id = res.data['id']

        # Chef replies to the comment
        self.client.force_authenticate(user=self.chef)
        res = self.client.post(comments_url, {
            'text': 'Thank you!',
            'parent': comment_id,
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Get comments and verify structure
        res = self.client.get(comments_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # One top-level comment

        top_comment = res.data[0]
        self.assertEqual(top_comment['text'], 'Great recipe!')
        self.assertEqual(len(top_comment['replies']), 1)
        self.assertEqual(top_comment['replies'][0]['text'], 'Thank you!')

    def test_anonymous_can_read_comments(self):
        """Test that anonymous users can read comments."""
        # Create a comment
        Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='Public comment',
        )

        # Anonymous user reads comments
        comments_url = reverse('recipe:recipe-comments', args=[self.recipe.id])
        res = self.client.get(comments_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['text'], 'Public comment')

    def test_anonymous_cannot_interact(self):
        """Test that anonymous users cannot rate, favorite, or comment."""
        rate_url = reverse('recipe:recipe-rate', args=[self.recipe.id])
        favorite_url = reverse('recipe:recipe-favorite', args=[self.recipe.id])
        comments_url = reverse('recipe:recipe-comments', args=[self.recipe.id])

        # Try to rate
        res = self.client.post(rate_url, {'score': 5})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try to favorite
        res = self.client.post(favorite_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try to comment
        res = self.client.post(comments_url, {'text': 'Test'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
