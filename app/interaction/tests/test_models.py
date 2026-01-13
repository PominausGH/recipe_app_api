from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from recipe.models import Recipe
from interaction.models import Rating, Favorite, Comment, Follow, FollowRequest, Block


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


class CommentModelTests(TestCase):
    """Tests for Comment model."""

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

    def test_create_comment(self):
        """Test creating a comment is successful."""
        comment = Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='This is a great recipe!',
        )

        self.assertEqual(comment.text, 'This is a great recipe!')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.recipe, self.recipe)
        self.assertIsNone(comment.parent)

    def test_nested_comment(self):
        """Test creating a reply to a comment."""
        parent_comment = Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='Original comment',
        )
        reply = Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='This is a reply',
            parent=parent_comment,
        )

        self.assertEqual(reply.parent, parent_comment)
        self.assertIn(reply, parent_comment.replies.all())

    def test_comment_cascade_delete_with_recipe(self):
        """Test comments deleted when recipe is deleted."""
        Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='Test comment',
        )

        self.recipe.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_str(self):
        """Test comment string representation."""
        comment = Comment.objects.create(
            user=self.user,
            recipe=self.recipe,
            text='Test comment',
        )
        expected = f'{self.user.email} on {self.recipe.title}'
        self.assertEqual(str(comment), expected)


class FollowModelTests(TestCase):
    """Tests for Follow model."""

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )

    def test_create_follow(self):
        """Test creating a follow relationship."""
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2,
        )
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)
        self.assertIsNotNone(follow.created_at)

    def test_follow_unique_constraint(self):
        """Test user can only follow another user once."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(ValidationError):
            Follow.objects.create(follower=self.user1, following=self.user2)

    def test_cannot_follow_self(self):
        """Test user cannot follow themselves."""
        with self.assertRaises(ValidationError):
            follow = Follow(follower=self.user1, following=self.user1)
            follow.full_clean()

    def test_follow_str(self):
        """Test follow string representation."""
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2,
        )
        expected = f'{self.user1.email} follows {self.user2.email}'
        self.assertEqual(str(follow), expected)


class FollowRequestModelTests(TestCase):
    """Tests for FollowRequest model."""

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
            is_private=True,
        )

    def test_create_follow_request(self):
        """Test creating a follow request."""
        request = FollowRequest.objects.create(
            requester=self.user1,
            target=self.user2,
        )
        self.assertEqual(request.requester, self.user1)
        self.assertEqual(request.target, self.user2)
        self.assertEqual(request.status, 'pending')

    def test_follow_request_unique_constraint(self):
        """Test only one pending request per user pair."""
        FollowRequest.objects.create(requester=self.user1, target=self.user2)
        with self.assertRaises(IntegrityError):
            FollowRequest.objects.create(requester=self.user1, target=self.user2)

    def test_follow_request_str(self):
        """Test follow request string representation."""
        request = FollowRequest.objects.create(
            requester=self.user1,
            target=self.user2,
        )
        expected = f'{self.user1.email} requested to follow {self.user2.email}'
        self.assertEqual(str(request), expected)


class BlockModelTests(TestCase):
    """Tests for Block model."""

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )

    def test_create_block(self):
        """Test creating a block."""
        block = Block.objects.create(
            user=self.user1,
            blocked_user=self.user2,
        )
        self.assertEqual(block.user, self.user1)
        self.assertEqual(block.blocked_user, self.user2)

    def test_block_unique_constraint(self):
        """Test user can only block another user once."""
        Block.objects.create(user=self.user1, blocked_user=self.user2)
        with self.assertRaises(ValidationError):
            Block.objects.create(user=self.user1, blocked_user=self.user2)

    def test_cannot_block_self(self):
        """Test user cannot block themselves."""
        with self.assertRaises(ValidationError):
            block = Block(user=self.user1, blocked_user=self.user1)
            block.full_clean()

    def test_block_str(self):
        """Test block string representation."""
        block = Block.objects.create(
            user=self.user1,
            blocked_user=self.user2,
        )
        expected = f'{self.user1.email} blocked {self.user2.email}'
        self.assertEqual(str(block), expected)
