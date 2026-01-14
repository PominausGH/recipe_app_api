from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification,
)


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


class FollowAPITests(TestCase):
    """Tests for follow API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )
        self.private_user = get_user_model().objects.create_user(
            email='private@example.com',
            password='testpass123',
            is_private=True,
        )

    def test_follow_user(self):
        """Test following a public user."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-follow', kwargs={'pk': self.user2.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follow.objects.filter(
                follower=self.user1,
                following=self.user2
            ).exists()
        )

    def test_follow_private_user_creates_request(self):
        """Test following private user creates follow request."""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            'interaction:user-follow', kwargs={'pk': self.private_user.id}
        )
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(
            FollowRequest.objects.filter(
                requester=self.user1,
                target=self.private_user
            ).exists()
        )

    def test_unfollow_user(self):
        """Test unfollowing a user."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-follow', kwargs={'pk': self.user2.id})
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Follow.objects.filter(
                follower=self.user1,
                following=self.user2
            ).exists()
        )

    def test_list_followers(self):
        """Test listing user's followers."""
        Follow.objects.create(follower=self.user2, following=self.user1)
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            'interaction:user-followers', kwargs={'pk': self.user1.id}
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_list_following(self):
        """Test listing who user follows."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            'interaction:user-following', kwargs={'pk': self.user1.id}
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_cannot_follow_self(self):
        """Test user cannot follow themselves."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-follow', kwargs={'pk': self.user1.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blocked_user_cannot_follow(self):
        """Test blocked user cannot follow blocker."""
        from interaction.models import Block
        Block.objects.create(user=self.user2, blocked_user=self.user1)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-follow', kwargs={'pk': self.user2.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_follow_user_twice(self):
        """Test cannot follow user already following."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-follow', kwargs={'pk': self.user2.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class FollowRequestAPITests(TestCase):
    """Tests for follow request management."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            is_private=True,
        )
        self.requester = get_user_model().objects.create_user(
            email='requester@example.com',
            password='testpass123',
        )

    def test_list_follow_requests(self):
        """Test listing pending follow requests."""
        FollowRequest.objects.create(
            requester=self.requester,
            target=self.user,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-follow-requests')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_accept_follow_request(self):
        """Test accepting a follow request."""
        request = FollowRequest.objects.create(
            requester=self.requester,
            target=self.user,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse(
            'interaction:user-accept-request', kwargs={'pk': request.id}
        )
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Follow.objects.filter(
                follower=self.requester,
                following=self.user
            ).exists()
        )
        request.refresh_from_db()
        self.assertEqual(request.status, 'approved')

    def test_reject_follow_request(self):
        """Test rejecting a follow request."""
        request = FollowRequest.objects.create(
            requester=self.requester,
            target=self.user,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse(
            'interaction:user-reject-request', kwargs={'pk': request.id}
        )
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertEqual(request.status, 'rejected')

    def test_cannot_accept_other_users_request(self):
        """Test user cannot accept follow request sent to another user."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
            is_private=True,
        )
        request = FollowRequest.objects.create(
            requester=self.requester,
            target=other_user,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse(
            'interaction:user-accept-request', kwargs={'pk': request.id}
        )
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class BlockMuteAPITests(TestCase):
    """Tests for block and mute endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )

    def test_block_user(self):
        """Test blocking a user."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-block', kwargs={'pk': self.user2.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Block.objects.filter(
                user=self.user1,
                blocked_user=self.user2
            ).exists()
        )

    def test_block_removes_follow_both_directions(self):
        """Test blocking removes follows in both directions."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.create(follower=self.user2, following=self.user1)

        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-block', kwargs={'pk': self.user2.id})
        self.client.post(url)

        self.assertFalse(
            Follow.objects.filter(
                follower=self.user1, following=self.user2
            ).exists()
        )
        self.assertFalse(
            Follow.objects.filter(
                follower=self.user2, following=self.user1
            ).exists()
        )

    def test_unblock_user(self):
        """Test unblocking a user."""
        Block.objects.create(user=self.user1, blocked_user=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-block', kwargs={'pk': self.user2.id})
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_mute_user(self):
        """Test muting a user."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-mute', kwargs={'pk': self.user2.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Mute.objects.filter(
                user=self.user1,
                muted_user=self.user2
            ).exists()
        )

    def test_unmute_user(self):
        """Test unmuting a user."""
        Mute.objects.create(user=self.user1, muted_user=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-mute', kwargs={'pk': self.user2.id})
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_blocked_users(self):
        """Test listing blocked users."""
        Block.objects.create(user=self.user1, blocked_user=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-blocked-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_list_muted_users(self):
        """Test listing muted users."""
        Mute.objects.create(user=self.user1, muted_user=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-muted-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_cannot_block_self(self):
        """Test user cannot block themselves."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-block', kwargs={'pk': self.user1.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_mute_self(self):
        """Test user cannot mute themselves."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-mute', kwargs={'pk': self.user1.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class NotificationAPITests(TestCase):
    """Tests for notification endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.actor = get_user_model().objects.create_user(
            email='actor@example.com',
            password='testpass123',
        )

    def test_list_notifications(self):
        """Test listing notifications."""
        Notification.objects.create(
            recipient=self.user,
            actor=self.actor,
            verb='followed',
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:notification-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_mark_notification_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.user,
            actor=self.actor,
            verb='followed',
        )
        self.client.force_authenticate(user=self.user)
        url = reverse(
            'interaction:notification-mark-read',
            kwargs={'pk': notification.id},
        )
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_read(self):
        """Test marking all notifications as read."""
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb='followed'
        )
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb='rated'
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:notification-mark-all-read')
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        unread = Notification.objects.filter(
            recipient=self.user, is_read=False
        ).count()
        self.assertEqual(unread, 0)

    def test_unread_count(self):
        """Test getting unread notification count."""
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb='followed'
        )
        Notification.objects.create(
            recipient=self.user, actor=self.actor, verb='rated'
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:notification-unread-count')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)

    def test_list_notifications_requires_auth(self):
        """Test authentication required to list notifications."""
        url = reverse('interaction:notification-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_mark_other_users_notification_read(self):
        """Test cannot mark another user's notification as read."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
        )
        notification = Notification.objects.create(
            recipient=other_user,
            actor=self.actor,
            verb='followed',
        )
        self.client.force_authenticate(user=self.user)
        url = reverse(
            'interaction:notification-mark-read',
            kwargs={'pk': notification.id},
        )
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class FeedAPITests(TestCase):
    """Tests for feed API endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.followed_user = get_user_model().objects.create_user(
            email='followed@example.com',
            password='testpass123',
        )
        Follow.objects.create(follower=self.user, following=self.followed_user)

    def test_get_feed(self):
        """Test getting activity feed."""
        Recipe.objects.create(
            author=self.followed_user,
            title='Test Recipe',
            instructions='Test',
            is_published=True,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:feed-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_feed_requires_auth(self):
        """Test feed requires authentication."""
        url = reverse('interaction:feed-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_feed_with_order_param(self):
        """Test feed with order param returns items chronologically."""
        from recipe.models import Recipe
        Recipe.objects.create(
            author=self.followed_user,
            title='First Recipe',
            instructions='Test',
            is_published=True,
        )
        Recipe.objects.create(
            author=self.followed_user,
            title='Second Recipe',
            instructions='Test',
            is_published=True,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:feed-list') + '?order=chronological'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        # Second recipe should be first (reverse chronological)
        self.assertEqual(
            res.data['results'][0]['recipe']['title'], 'Second Recipe'
        )
        self.assertEqual(
            res.data['results'][1]['recipe']['title'], 'First Recipe'
        )


class DiscoveryAPITests(TestCase):
    """Tests for user discovery endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User',
        )
        self.other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='testpass123',
            name='Other User',
        )

    def test_search_users(self):
        """Test searching users by name."""
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-search') + '?q=Other'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_search_users_by_email(self):
        """Test searching users by email."""
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-search') + '?q=other@'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_search_excludes_self(self):
        """Test search excludes the current user."""
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-search') + '?q=Test'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)

    def test_search_requires_min_query_length(self):
        """Test search requires at least 2 characters."""
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-search') + '?q=O'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)

    def test_popular_users(self):
        """Test getting popular users."""
        # Create followers for other_user
        for i in range(5):
            follower = get_user_model().objects.create_user(
                email=f'follower{i}@example.com',
                password='testpass123',
            )
            Follow.objects.create(follower=follower, following=self.other_user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-popular')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.data['results']), 0)

    def test_popular_users_ordered_by_follower_count(self):
        """Test popular users are ordered by follower count."""
        # Create followers for other_user (5 followers)
        for i in range(5):
            follower = get_user_model().objects.create_user(
                email=f'follower{i}@example.com',
                password='testpass123',
            )
            Follow.objects.create(follower=follower, following=self.other_user)

        # Create a third user with more followers (7 followers)
        most_popular = get_user_model().objects.create_user(
            email='popular@example.com',
            password='testpass123',
            name='Popular User',
        )
        for i in range(7):
            follower = get_user_model().objects.create_user(
                email=f'pop_follower{i}@example.com',
                password='testpass123',
            )
            Follow.objects.create(follower=follower, following=most_popular)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-popular')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Most popular user should be first
        self.assertEqual(res.data['results'][0]['id'], most_popular.id)

    def test_suggested_users(self):
        """Test getting suggested users based on who you follow."""
        # User follows other_user
        Follow.objects.create(follower=self.user, following=self.other_user)

        # other_user follows a third user
        third_user = get_user_model().objects.create_user(
            email='third@example.com',
            password='testpass123',
            name='Third User',
        )
        Follow.objects.create(follower=self.other_user, following=third_user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-suggested')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Third user should be suggested
        user_ids = [u['id'] for u in res.data['results']]
        self.assertIn(third_user.id, user_ids)

    def test_suggested_excludes_already_following(self):
        """Test suggested users excludes users already followed."""
        # User follows other_user
        Follow.objects.create(follower=self.user, following=self.other_user)

        # other_user follows third_user
        third_user = get_user_model().objects.create_user(
            email='third@example.com',
            password='testpass123',
            name='Third User',
        )
        Follow.objects.create(follower=self.other_user, following=third_user)

        # User also follows third_user directly
        Follow.objects.create(follower=self.user, following=third_user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-suggested')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Third user should NOT be suggested since already following
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(third_user.id, user_ids)

    def test_suggested_requires_auth(self):
        """Test suggested users requires authentication."""
        url = reverse('interaction:user-suggested')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_requires_auth(self):
        """Test search requires authentication."""
        url = reverse('interaction:user-search') + '?q=Other'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_excludes_blocked_users(self):
        """Test search excludes users who blocked the current user."""
        # Create a user who blocks self.user
        blocker = get_user_model().objects.create_user(
            email='blocker@example.com',
            password='testpass123',
            name='Blocker User',
        )
        Block.objects.create(user=blocker, blocked_user=self.user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-search') + '?q=Blocker'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(blocker.id, user_ids)

    def test_search_excludes_users_blocked_by_current_user(self):
        """Test search excludes users the current user has blocked."""
        # User blocks other_user
        Block.objects.create(user=self.user, blocked_user=self.other_user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-search') + '?q=Other'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(self.other_user.id, user_ids)

    def test_popular_excludes_blocked_users(self):
        """Test popular excludes users who blocked the current user."""
        # Create a popular user who blocks self.user
        blocker = get_user_model().objects.create_user(
            email='blocker@example.com',
            password='testpass123',
            name='Blocker User',
        )
        # Give them followers to make them popular
        for i in range(5):
            follower = get_user_model().objects.create_user(
                email=f'follower{i}@example.com',
                password='testpass123',
            )
            Follow.objects.create(follower=follower, following=blocker)

        Block.objects.create(user=blocker, blocked_user=self.user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-popular')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(blocker.id, user_ids)

    def test_popular_excludes_users_blocked_by_current_user(self):
        """Test popular excludes users the current user has blocked."""
        # Give other_user followers to make them popular
        for i in range(5):
            follower = get_user_model().objects.create_user(
                email=f'follower{i}@example.com',
                password='testpass123',
            )
            Follow.objects.create(follower=follower, following=self.other_user)

        Block.objects.create(user=self.user, blocked_user=self.other_user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-popular')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(self.other_user.id, user_ids)

    def test_popular_unauthenticated(self):
        """Test popular endpoint works without authentication."""
        # Create followers for other_user
        for i in range(3):
            follower = get_user_model().objects.create_user(
                email=f'follower{i}@example.com',
                password='testpass123',
            )
            Follow.objects.create(follower=follower, following=self.other_user)

        url = reverse('interaction:user-popular')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.data['results']), 0)

    def test_suggested_excludes_blocked_users(self):
        """Test suggested excludes users who blocked the current user."""
        # User follows other_user
        Follow.objects.create(follower=self.user, following=self.other_user)

        # other_user follows third_user, who blocks self.user
        third_user = get_user_model().objects.create_user(
            email='third@example.com',
            password='testpass123',
            name='Third User',
        )
        Follow.objects.create(follower=self.other_user, following=third_user)
        Block.objects.create(user=third_user, blocked_user=self.user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-suggested')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(third_user.id, user_ids)

    def test_suggested_excludes_users_blocked_by_current_user(self):
        """Test suggested excludes users the current user has blocked."""
        # User follows other_user
        Follow.objects.create(follower=self.user, following=self.other_user)

        # other_user follows third_user
        third_user = get_user_model().objects.create_user(
            email='third@example.com',
            password='testpass123',
            name='Third User',
        )
        Follow.objects.create(follower=self.other_user, following=third_user)

        # User blocks third_user
        Block.objects.create(user=self.user, blocked_user=third_user)

        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-suggested')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_ids = [u['id'] for u in res.data['results']]
        self.assertNotIn(third_user.id, user_ids)

    def test_suggested_empty_when_not_following_anyone(self):
        """Test suggested returns empty when user follows no one."""
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:user-suggested')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)
