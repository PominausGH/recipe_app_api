# Social Features Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add social features including user following, activity feeds, notifications, discovery, and badges to the Recipe App.

**Architecture:** Extend the existing `interaction` app with new models for Follow, Block, Mute, Notification, and Badge. Add new ViewSets for social endpoints. Create services for feed generation, notification dispatch, and badge awards.

**Tech Stack:** Django REST Framework, PostgreSQL, React (frontend)

---

## Phase 1: Core Social Models

### Task 1.1: Add User Model Extensions

**Files:**
- Modify: `app/core/models.py`
- Test: `app/core/tests/test_models.py`

**Step 1: Write failing test for is_private field**

Add to `app/core/tests/test_models.py`:

```python
class UserPrivacyTests(TestCase):
    """Tests for user privacy fields."""

    def test_user_is_private_default_false(self):
        """Test is_private defaults to False."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.assertFalse(user.is_private)

    def test_user_is_verified_default_false(self):
        """Test is_verified defaults to False."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.assertFalse(user.is_verified)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test core.tests.test_models.UserPrivacyTests -v 2"
```

Expected: FAIL with "User has no attribute 'is_private'"

**Step 3: Add fields to User model**

In `app/core/models.py`, add to User class:

```python
is_private = models.BooleanField(default=False)
is_verified = models.BooleanField(default=False)
```

**Step 4: Create and run migration**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations core"
docker-compose run --rm app sh -c "python manage.py migrate"
```

**Step 5: Run test to verify it passes**

```bash
docker-compose run --rm app sh -c "python manage.py test core.tests.test_models.UserPrivacyTests -v 2"
```

**Step 6: Commit**

```bash
git add app/core/models.py app/core/migrations/ app/core/tests/test_models.py
git commit -m "feat(core): add is_private and is_verified fields to User"
```

---

### Task 1.2: Create Follow Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests for Follow model**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import Rating, Favorite, Comment, Follow


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
        with self.assertRaises(IntegrityError):
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
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.FollowModelTests -v 2"
```

**Step 3: Add Follow model**

Add to `app/interaction/models.py`:

```python
class Follow(models.Model):
    """User following another user."""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_set',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']
        ordering = ['-created_at']

    def clean(self):
        if self.follower == self.following:
            raise ValidationError('Users cannot follow themselves.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.follower.email} follows {self.following.email}'
```

Add import at top: `from django.core.exceptions import ValidationError`

**Step 4: Create migration**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction"
docker-compose run --rm app sh -c "python manage.py migrate"
```

**Step 5: Run test to verify it passes**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.FollowModelTests -v 2"
```

**Step 6: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add Follow model"
```

---

### Task 1.3: Create FollowRequest Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import Rating, Favorite, Comment, Follow, FollowRequest


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
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.FollowRequestModelTests -v 2"
```

**Step 3: Add FollowRequest model**

Add to `app/interaction/models.py`:

```python
class FollowRequest(models.Model):
    """Pending follow request for private accounts."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_follow_requests',
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_follow_requests',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['requester', 'target']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.requester.email} requested to follow {self.target.email}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.FollowRequestModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add FollowRequest model"
```

---

### Task 1.4: Create Block Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import Rating, Favorite, Comment, Follow, FollowRequest, Block


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
        with self.assertRaises(IntegrityError):
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
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.BlockModelTests -v 2"
```

**Step 3: Add Block model**

Add to `app/interaction/models.py`:

```python
class Block(models.Model):
    """User blocking another user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocking',
    )
    blocked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'blocked_user']
        ordering = ['-created_at']

    def clean(self):
        if self.user == self.blocked_user:
            raise ValidationError('Users cannot block themselves.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email} blocked {self.blocked_user.email}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.BlockModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add Block model"
```

---

### Task 1.5: Create Mute Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import Rating, Favorite, Comment, Follow, FollowRequest, Block, Mute


class MuteModelTests(TestCase):
    """Tests for Mute model."""

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )

    def test_create_mute(self):
        """Test creating a mute."""
        mute = Mute.objects.create(
            user=self.user1,
            muted_user=self.user2,
        )
        self.assertEqual(mute.user, self.user1)
        self.assertEqual(mute.muted_user, self.user2)

    def test_mute_unique_constraint(self):
        """Test user can only mute another user once."""
        Mute.objects.create(user=self.user1, muted_user=self.user2)
        with self.assertRaises(IntegrityError):
            Mute.objects.create(user=self.user1, muted_user=self.user2)

    def test_mute_str(self):
        """Test mute string representation."""
        mute = Mute.objects.create(
            user=self.user1,
            muted_user=self.user2,
        )
        expected = f'{self.user1.email} muted {self.user2.email}'
        self.assertEqual(str(mute), expected)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.MuteModelTests -v 2"
```

**Step 3: Add Mute model**

Add to `app/interaction/models.py`:

```python
class Mute(models.Model):
    """User muting another user (hides from feed)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='muting',
    )
    muted_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='muted_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'muted_user']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} muted {self.muted_user.email}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.MuteModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add Mute model"
```

---

## Phase 2: Notification & Preference Models

### Task 2.1: Create Notification Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification
)


class NotificationModelTests(TestCase):
    """Tests for Notification model."""

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123',
        )

    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            verb='followed',
        )
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.actor, self.user2)
        self.assertEqual(notification.verb, 'followed')
        self.assertFalse(notification.is_read)

    def test_notification_with_target(self):
        """Test notification with target object."""
        recipe = Recipe.objects.create(
            author=self.user1,
            title='Test Recipe',
            instructions='Test',
            is_published=True,
        )
        notification = Notification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            verb='rated',
            target_type='recipe',
            target_id=recipe.id,
        )
        self.assertEqual(notification.target_type, 'recipe')
        self.assertEqual(notification.target_id, recipe.id)

    def test_notification_str(self):
        """Test notification string representation."""
        notification = Notification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            verb='followed',
        )
        expected = f'{self.user2.email} followed {self.user1.email}'
        self.assertEqual(str(notification), expected)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.NotificationModelTests -v 2"
```

**Step 3: Add Notification model**

Add to `app/interaction/models.py`:

```python
class Notification(models.Model):
    """User notification."""
    VERB_CHOICES = [
        ('followed', 'Followed'),
        ('follow_request', 'Follow Request'),
        ('rated', 'Rated'),
        ('commented', 'Commented'),
        ('favorited', 'Favorited'),
        ('posted_recipe', 'Posted Recipe'),
        ('badge_awarded', 'Badge Awarded'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actions',
        null=True,
        blank=True,
    )
    verb = models.CharField(max_length=20, choices=VERB_CHOICES)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.actor.email} {self.verb} {self.recipient.email}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.NotificationModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add Notification model"
```

---

### Task 2.2: Create NotificationPreference Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification, NotificationPreference
)


class NotificationPreferenceModelTests(TestCase):
    """Tests for NotificationPreference model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

    def test_create_notification_preference(self):
        """Test creating notification preferences."""
        prefs = NotificationPreference.objects.create(user=self.user)
        self.assertTrue(prefs.notify_new_follower)
        self.assertTrue(prefs.notify_recipe_comment)
        self.assertEqual(prefs.email_digest, 'none')

    def test_preference_one_to_one(self):
        """Test only one preference per user."""
        NotificationPreference.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            NotificationPreference.objects.create(user=self.user)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.NotificationPreferenceModelTests -v 2"
```

**Step 3: Add NotificationPreference model**

Add to `app/interaction/models.py`:

```python
class NotificationPreference(models.Model):
    """User notification preferences."""
    EMAIL_DIGEST_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    notify_new_follower = models.BooleanField(default=True)
    notify_follow_request = models.BooleanField(default=True)
    notify_recipe_comment = models.BooleanField(default=True)
    notify_recipe_rating = models.BooleanField(default=True)
    notify_comment_reply = models.BooleanField(default=True)
    notify_following_new_recipe = models.BooleanField(default=True)
    email_digest = models.CharField(
        max_length=10,
        choices=EMAIL_DIGEST_CHOICES,
        default='none',
    )

    def __str__(self):
        return f'Notification preferences for {self.user.email}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.NotificationPreferenceModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add NotificationPreference model"
```

---

### Task 2.3: Create FeedPreference Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification, NotificationPreference, FeedPreference
)


class FeedPreferenceModelTests(TestCase):
    """Tests for FeedPreference model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

    def test_create_feed_preference(self):
        """Test creating feed preferences."""
        prefs = FeedPreference.objects.create(user=self.user)
        self.assertTrue(prefs.show_recipes)
        self.assertTrue(prefs.show_ratings)
        self.assertFalse(prefs.show_comments)
        self.assertEqual(prefs.feed_order, 'chronological')

    def test_preference_one_to_one(self):
        """Test only one preference per user."""
        FeedPreference.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            FeedPreference.objects.create(user=self.user)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.FeedPreferenceModelTests -v 2"
```

**Step 3: Add FeedPreference model**

Add to `app/interaction/models.py`:

```python
class FeedPreference(models.Model):
    """User feed preferences."""
    FEED_ORDER_CHOICES = [
        ('chronological', 'Chronological'),
        ('algorithmic', 'Algorithmic'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_preferences',
    )
    show_recipes = models.BooleanField(default=True)
    show_ratings = models.BooleanField(default=True)
    show_comments = models.BooleanField(default=False)
    show_favorites = models.BooleanField(default=False)
    feed_order = models.CharField(
        max_length=15,
        choices=FEED_ORDER_CHOICES,
        default='chronological',
    )

    def __str__(self):
        return f'Feed preferences for {self.user.email}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.FeedPreferenceModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add FeedPreference model"
```

---

## Phase 3: Badge Models

### Task 3.1: Create Badge Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification, NotificationPreference,
    FeedPreference, Badge
)


class BadgeModelTests(TestCase):
    """Tests for Badge model."""

    def test_create_badge(self):
        """Test creating a badge."""
        badge = Badge.objects.create(
            name='Rising Chef',
            slug='rising-chef',
            description='Published 10 recipes',
            icon='chef-hat',
            badge_type='achievement',
            criteria={'type': 'recipe_count', 'threshold': 10},
        )
        self.assertEqual(badge.name, 'Rising Chef')
        self.assertEqual(badge.badge_type, 'achievement')

    def test_create_verified_badge(self):
        """Test creating a verified badge (no criteria)."""
        badge = Badge.objects.create(
            name='Verified',
            slug='verified',
            description='Verified account',
            icon='checkmark',
            badge_type='verified',
        )
        self.assertEqual(badge.badge_type, 'verified')
        self.assertIsNone(badge.criteria)

    def test_badge_str(self):
        """Test badge string representation."""
        badge = Badge.objects.create(
            name='Rising Chef',
            slug='rising-chef',
            description='Published 10 recipes',
            icon='chef-hat',
            badge_type='achievement',
        )
        self.assertEqual(str(badge), 'Rising Chef')
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.BadgeModelTests -v 2"
```

**Step 3: Add Badge model**

Add to `app/interaction/models.py`:

```python
class Badge(models.Model):
    """Badge definition."""
    BADGE_TYPE_CHOICES = [
        ('verified', 'Verified'),
        ('achievement', 'Achievement'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=50)
    badge_type = models.CharField(max_length=15, choices=BADGE_TYPE_CHOICES)
    criteria = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.BadgeModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add Badge model"
```

---

### Task 3.2: Create UserBadge Model

**Files:**
- Modify: `app/interaction/models.py`
- Test: `app/interaction/tests/test_models.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_models.py`:

```python
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification, NotificationPreference,
    FeedPreference, Badge, UserBadge
)


class UserBadgeModelTests(TestCase):
    """Tests for UserBadge model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.badge = Badge.objects.create(
            name='Rising Chef',
            slug='rising-chef',
            description='Published 10 recipes',
            icon='chef-hat',
            badge_type='achievement',
        )

    def test_create_user_badge(self):
        """Test awarding a badge to user."""
        user_badge = UserBadge.objects.create(
            user=self.user,
            badge=self.badge,
        )
        self.assertEqual(user_badge.user, self.user)
        self.assertEqual(user_badge.badge, self.badge)
        self.assertIsNone(user_badge.awarded_by)

    def test_user_badge_unique(self):
        """Test user can only have badge once."""
        UserBadge.objects.create(user=self.user, badge=self.badge)
        with self.assertRaises(IntegrityError):
            UserBadge.objects.create(user=self.user, badge=self.badge)

    def test_user_badge_str(self):
        """Test user badge string representation."""
        user_badge = UserBadge.objects.create(
            user=self.user,
            badge=self.badge,
        )
        expected = f'{self.user.email} earned {self.badge.name}'
        self.assertEqual(str(user_badge), expected)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.UserBadgeModelTests -v 2"
```

**Step 3: Add UserBadge model**

Add to `app/interaction/models.py`:

```python
class UserBadge(models.Model):
    """Badge awarded to a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges',
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='awarded_to',
    )
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='badges_awarded',
    )

    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-awarded_at']

    def __str__(self):
        return f'{self.user.email} earned {self.badge.name}'
```

**Step 4: Create migration and run tests**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations interaction && python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_models.UserBadgeModelTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/models.py app/interaction/migrations/ app/interaction/tests/test_models.py
git commit -m "feat(interaction): add UserBadge model"
```

---

## Phase 4: Follow API Endpoints

### Task 4.1: Create Follow Serializers

**Files:**
- Modify: `app/interaction/serializers.py`

**Step 1: Add serializers**

Add to `app/interaction/serializers.py`:

```python
from interaction.models import (
    Rating, Favorite, Comment, Follow, FollowRequest,
    Block, Mute, Notification, NotificationPreference,
    FeedPreference, Badge, UserBadge
)


class UserSummarySerializer(serializers.Serializer):
    """Lightweight user serializer for social features."""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    profile_photo = serializers.ImageField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships."""
    follower = UserSummarySerializer(read_only=True)
    following = UserSummarySerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'following', 'created_at']


class FollowRequestSerializer(serializers.ModelSerializer):
    """Serializer for follow requests."""
    requester = UserSummarySerializer(read_only=True)
    target = UserSummarySerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ['id', 'requester', 'target', 'status', 'created_at']
        read_only_fields = ['id', 'requester', 'target', 'created_at']
```

**Step 2: Commit**

```bash
git add app/interaction/serializers.py
git commit -m "feat(interaction): add Follow and FollowRequest serializers"
```

---

### Task 4.2: Create User ViewSet with Follow Actions

**Files:**
- Create: `app/interaction/views.py`
- Create: `app/interaction/urls.py`
- Modify: `app/app/urls.py`
- Test: `app/interaction/tests/test_api.py`

**Step 1: Write failing tests**

Create/update `app/interaction/tests/test_api.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from interaction.models import Follow, FollowRequest


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
        url = reverse('interaction:user-follow', kwargs={'pk': self.private_user.id})
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
        url = reverse('interaction:user-followers', kwargs={'pk': self.user1.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_list_following(self):
        """Test listing who user follows."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-following', kwargs={'pk': self.user1.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_cannot_follow_self(self):
        """Test user cannot follow themselves."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('interaction:user-follow', kwargs={'pk': self.user1.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.FollowAPITests -v 2"
```

**Step 3: Create views.py**

Create `app/interaction/views.py`:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from interaction.models import (
    Follow, FollowRequest, Block, Mute,
    Notification, NotificationPreference, FeedPreference,
    Badge, UserBadge
)
from interaction.serializers import (
    FollowSerializer, FollowRequestSerializer, UserSummarySerializer
)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.GenericViewSet):
    """ViewSet for user social actions."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

    def get_queryset(self):
        return get_user_model().objects.all()

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """Follow or unfollow a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if blocked
        if Block.objects.filter(user=target_user, blocked_user=request.user).exists():
            return Response(
                {'error': 'Unable to follow this user.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'DELETE':
            Follow.objects.filter(
                follower=request.user,
                following=target_user
            ).delete()
            FollowRequest.objects.filter(
                requester=request.user,
                target=target_user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # POST - follow
        if Follow.objects.filter(follower=request.user, following=target_user).exists():
            return Response(
                {'error': 'Already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if target_user.is_private:
            follow_request, created = FollowRequest.objects.get_or_create(
                requester=request.user,
                target=target_user,
                defaults={'status': 'pending'}
            )
            serializer = FollowRequestSerializer(follow_request)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        follow = Follow.objects.create(
            follower=request.user,
            following=target_user
        )
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """List user's followers."""
        user = get_object_or_404(get_user_model(), pk=pk)
        follows = Follow.objects.filter(following=user).select_related('follower')
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """List who user follows."""
        user = get_object_or_404(get_user_model(), pk=pk)
        follows = Follow.objects.filter(follower=user).select_related('following')
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

**Step 4: Create urls.py**

Create `app/interaction/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interaction import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

app_name = 'interaction'

urlpatterns = [
    path('', include(router.urls)),
]
```

**Step 5: Update main urls.py**

Modify `app/app/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipe.urls')),
    path('api/', include('interaction.urls')),
    path('api/auth/', include('core.urls')),
]
```

**Step 6: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.FollowAPITests -v 2"
```

**Step 7: Commit**

```bash
git add app/interaction/views.py app/interaction/urls.py app/app/urls.py app/interaction/tests/test_api.py
git commit -m "feat(interaction): add follow/unfollow API endpoints"
```

---

### Task 4.3: Add Follow Request Management

**Files:**
- Modify: `app/interaction/views.py`
- Test: `app/interaction/tests/test_api.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_api.py`:

```python
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
        url = reverse('interaction:user-accept-request', kwargs={'pk': request.id})
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
        url = reverse('interaction:user-reject-request', kwargs={'pk': request.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertEqual(request.status, 'rejected')
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.FollowRequestAPITests -v 2"
```

**Step 3: Add follow request actions to views**

Add to `app/interaction/views.py` UserViewSet:

```python
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            url_path='me/follow-requests', url_name='follow-requests')
    def follow_requests(self, request):
        """List pending follow requests for current user."""
        requests = FollowRequest.objects.filter(
            target=request.user,
            status='pending'
        ).select_related('requester')
        page = self.paginate_queryset(requests)
        serializer = FollowRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],
            url_path='accept', url_name='accept-request')
    def accept_request(self, request, pk=None):
        """Accept a follow request."""
        follow_request = get_object_or_404(
            FollowRequest,
            pk=pk,
            target=request.user,
            status='pending'
        )
        follow_request.status = 'approved'
        follow_request.save()

        Follow.objects.get_or_create(
            follower=follow_request.requester,
            following=request.user
        )

        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],
            url_path='reject', url_name='reject-request')
    def reject_request(self, request, pk=None):
        """Reject a follow request."""
        follow_request = get_object_or_404(
            FollowRequest,
            pk=pk,
            target=request.user,
            status='pending'
        )
        follow_request.status = 'rejected'
        follow_request.save()

        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data)
```

**Step 4: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.FollowRequestAPITests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/views.py app/interaction/tests/test_api.py
git commit -m "feat(interaction): add follow request accept/reject endpoints"
```

---

## Phase 5: Block & Mute API

### Task 5.1: Add Block/Mute Serializers and Endpoints

**Files:**
- Modify: `app/interaction/serializers.py`
- Modify: `app/interaction/views.py`
- Test: `app/interaction/tests/test_api.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_api.py`:

```python
from interaction.models import Follow, FollowRequest, Block, Mute


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

        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())
        self.assertFalse(Follow.objects.filter(follower=self.user2, following=self.user1).exists())

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
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.BlockMuteAPITests -v 2"
```

**Step 3: Add serializers**

Add to `app/interaction/serializers.py`:

```python
class BlockSerializer(serializers.ModelSerializer):
    """Serializer for blocks."""
    blocked_user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Block
        fields = ['id', 'blocked_user', 'created_at']
        read_only_fields = ['id', 'created_at']


class MuteSerializer(serializers.ModelSerializer):
    """Serializer for mutes."""
    muted_user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Mute
        fields = ['id', 'muted_user', 'created_at']
        read_only_fields = ['id', 'created_at']
```

**Step 4: Add block/mute actions to views**

Add to `app/interaction/views.py` UserViewSet:

```python
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def block(self, request, pk=None):
        """Block or unblock a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {'error': 'You cannot block yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            Block.objects.filter(
                user=request.user,
                blocked_user=target_user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # POST - block
        block, created = Block.objects.get_or_create(
            user=request.user,
            blocked_user=target_user
        )

        # Remove follows in both directions
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        Follow.objects.filter(follower=target_user, following=request.user).delete()
        FollowRequest.objects.filter(requester=request.user, target=target_user).delete()
        FollowRequest.objects.filter(requester=target_user, target=request.user).delete()

        from interaction.serializers import BlockSerializer
        serializer = BlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def mute(self, request, pk=None):
        """Mute or unmute a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {'error': 'You cannot mute yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            Mute.objects.filter(
                user=request.user,
                muted_user=target_user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        mute, created = Mute.objects.get_or_create(
            user=request.user,
            muted_user=target_user
        )

        from interaction.serializers import MuteSerializer
        serializer = MuteSerializer(mute)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            url_path='me/blocked', url_name='blocked-list')
    def blocked_list(self, request):
        """List blocked users."""
        blocks = Block.objects.filter(user=request.user).select_related('blocked_user')
        page = self.paginate_queryset(blocks)
        from interaction.serializers import BlockSerializer
        serializer = BlockSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            url_path='me/muted', url_name='muted-list')
    def muted_list(self, request):
        """List muted users."""
        mutes = Mute.objects.filter(user=request.user).select_related('muted_user')
        page = self.paginate_queryset(mutes)
        from interaction.serializers import MuteSerializer
        serializer = MuteSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

**Step 5: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.BlockMuteAPITests -v 2"
```

**Step 6: Commit**

```bash
git add app/interaction/serializers.py app/interaction/views.py app/interaction/tests/test_api.py
git commit -m "feat(interaction): add block and mute API endpoints"
```

---

## Phase 6: Notification API

### Task 6.1: Add Notification Serializers and Endpoints

**Files:**
- Modify: `app/interaction/serializers.py`
- Modify: `app/interaction/views.py`
- Test: `app/interaction/tests/test_api.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_api.py`:

```python
from interaction.models import Follow, FollowRequest, Block, Mute, Notification


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
        url = reverse('interaction:notification-mark-read', kwargs={'pk': notification.id})
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_read(self):
        """Test marking all notifications as read."""
        Notification.objects.create(recipient=self.user, actor=self.actor, verb='followed')
        Notification.objects.create(recipient=self.user, actor=self.actor, verb='rated')
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:notification-mark-all-read')
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)

    def test_unread_count(self):
        """Test getting unread notification count."""
        Notification.objects.create(recipient=self.user, actor=self.actor, verb='followed')
        Notification.objects.create(recipient=self.user, actor=self.actor, verb='rated')
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:notification-unread-count')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.NotificationAPITests -v 2"
```

**Step 3: Add notification serializer**

Add to `app/interaction/serializers.py`:

```python
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    actor = UserSummarySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'target_type', 'target_id', 'is_read', 'created_at']
        read_only_fields = ['id', 'actor', 'verb', 'target_type', 'target_id', 'created_at']
```

**Step 4: Add notification ViewSet**

Add to `app/interaction/views.py`:

```python
class NotificationViewSet(viewsets.GenericViewSet):
    """ViewSet for notifications."""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def list(self, request):
        """List notifications."""
        queryset = self.get_queryset().select_related('actor')
        page = self.paginate_queryset(queryset)
        from interaction.serializers import NotificationSerializer
        serializer = NotificationSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='read', url_name='mark-read')
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        notification.is_read = True
        notification.save()
        from interaction.serializers import NotificationSerializer
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='read', url_name='mark-all-read')
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['get'], url_path='unread-count', url_name='unread-count')
    def unread_count(self, request):
        """Get unread notification count."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
```

**Step 5: Update urls.py**

Update `app/interaction/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interaction import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('notifications', views.NotificationViewSet, basename='notification')

app_name = 'interaction'

urlpatterns = [
    path('', include(router.urls)),
]
```

**Step 6: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.NotificationAPITests -v 2"
```

**Step 7: Commit**

```bash
git add app/interaction/serializers.py app/interaction/views.py app/interaction/urls.py app/interaction/tests/test_api.py
git commit -m "feat(interaction): add notification API endpoints"
```

---

## Phase 7: Activity Feed

### Task 7.1: Create Feed Service

**Files:**
- Create: `app/interaction/services/__init__.py`
- Create: `app/interaction/services/feed.py`
- Test: `app/interaction/tests/test_services.py`

**Step 1: Write failing tests**

Create `app/interaction/tests/test_services.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Recipe
from interaction.models import Follow, Rating, Favorite, Mute, FeedPreference
from interaction.services.feed import FeedService


class FeedServiceTests(TestCase):
    """Tests for feed generation service."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.followed_user = get_user_model().objects.create_user(
            email='followed@example.com',
            password='testpass123',
        )
        Follow.objects.create(follower=self.user, following=self.followed_user)

    def test_feed_includes_followed_user_recipes(self):
        """Test feed includes recipes from followed users."""
        recipe = Recipe.objects.create(
            author=self.followed_user,
            title='Test Recipe',
            instructions='Test',
            is_published=True,
        )
        feed = FeedService.get_feed(self.user)

        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0]['type'], 'recipe')
        self.assertEqual(feed[0]['recipe'].id, recipe.id)

    def test_feed_excludes_muted_users(self):
        """Test feed excludes content from muted users."""
        Recipe.objects.create(
            author=self.followed_user,
            title='Test Recipe',
            instructions='Test',
            is_published=True,
        )
        Mute.objects.create(user=self.user, muted_user=self.followed_user)

        feed = FeedService.get_feed(self.user)
        self.assertEqual(len(feed), 0)

    def test_feed_respects_preferences(self):
        """Test feed respects user preferences."""
        recipe = Recipe.objects.create(
            author=self.followed_user,
            title='Test Recipe',
            instructions='Test',
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
        types = [item['type'] for item in feed]
        self.assertIn('recipe', types)
        self.assertNotIn('rating', types)

    def test_feed_chronological_order(self):
        """Test feed is in chronological order."""
        recipe1 = Recipe.objects.create(
            author=self.followed_user,
            title='First Recipe',
            instructions='Test',
            is_published=True,
        )
        recipe2 = Recipe.objects.create(
            author=self.followed_user,
            title='Second Recipe',
            instructions='Test',
            is_published=True,
        )

        feed = FeedService.get_feed(self.user, order='chronological')
        self.assertEqual(feed[0]['recipe'].id, recipe2.id)
        self.assertEqual(feed[1]['recipe'].id, recipe1.id)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_services.FeedServiceTests -v 2"
```

**Step 3: Create feed service**

Create `app/interaction/services/__init__.py`:

```python
from .feed import FeedService

__all__ = ['FeedService']
```

Create `app/interaction/services/feed.py`:

```python
from django.db.models import Q
from interaction.models import Follow, Mute, FeedPreference, Rating, Favorite, Comment
from recipe.models import Recipe


class FeedService:
    """Service for generating activity feeds."""

    @classmethod
    def get_feed(cls, user, order='chronological', limit=50):
        """Get activity feed for a user."""
        # Get users this user follows
        following_ids = Follow.objects.filter(
            follower=user
        ).values_list('following_id', flat=True)

        # Exclude muted users
        muted_ids = Mute.objects.filter(
            user=user
        ).values_list('muted_user_id', flat=True)

        active_following_ids = [
            uid for uid in following_ids if uid not in muted_ids
        ]

        # Get user preferences
        try:
            prefs = user.feed_preferences
        except FeedPreference.DoesNotExist:
            prefs = None

        feed_items = []

        # Get recipes
        if prefs is None or prefs.show_recipes:
            recipes = Recipe.objects.filter(
                author_id__in=active_following_ids,
                is_published=True,
            ).select_related('author').order_by('-created_at')[:limit]

            for recipe in recipes:
                feed_items.append({
                    'type': 'recipe',
                    'actor': recipe.author,
                    'recipe': recipe,
                    'created_at': recipe.created_at,
                })

        # Get ratings
        if prefs is None or prefs.show_ratings:
            ratings = Rating.objects.filter(
                user_id__in=active_following_ids,
            ).select_related('user', 'recipe').order_by('-created_at')[:limit]

            for rating in ratings:
                feed_items.append({
                    'type': 'rating',
                    'actor': rating.user,
                    'recipe': rating.recipe,
                    'score': rating.score,
                    'created_at': rating.created_at,
                })

        # Get favorites
        if prefs and prefs.show_favorites:
            favorites = Favorite.objects.filter(
                user_id__in=active_following_ids,
            ).select_related('user', 'recipe').order_by('-created_at')[:limit]

            for favorite in favorites:
                feed_items.append({
                    'type': 'favorite',
                    'actor': favorite.user,
                    'recipe': favorite.recipe,
                    'created_at': favorite.created_at,
                })

        # Sort by date
        if order == 'chronological':
            feed_items.sort(key=lambda x: x['created_at'], reverse=True)

        return feed_items[:limit]
```

**Step 4: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_services.FeedServiceTests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/services/ app/interaction/tests/test_services.py
git commit -m "feat(interaction): add feed generation service"
```

---

### Task 7.2: Add Feed API Endpoint

**Files:**
- Modify: `app/interaction/views.py`
- Modify: `app/interaction/serializers.py`
- Modify: `app/interaction/urls.py`
- Test: `app/interaction/tests/test_api.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_api.py`:

```python
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
        """Test feed with order parameter."""
        self.client.force_authenticate(user=self.user)
        url = reverse('interaction:feed-list') + '?order=chronological'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.FeedAPITests -v 2"
```

**Step 3: Add feed serializer**

Add to `app/interaction/serializers.py`:

```python
from recipe.serializers import RecipeListSerializer


class FeedItemSerializer(serializers.Serializer):
    """Serializer for feed items."""
    type = serializers.CharField()
    actor = UserSummarySerializer()
    recipe = RecipeListSerializer()
    score = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField()
```

**Step 4: Add feed ViewSet**

Add to `app/interaction/views.py`:

```python
from interaction.services.feed import FeedService


class FeedViewSet(viewsets.GenericViewSet):
    """ViewSet for activity feed."""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def list(self, request):
        """Get activity feed."""
        order = request.query_params.get('order', 'chronological')
        feed_items = FeedService.get_feed(request.user, order=order)

        # Manual pagination
        page = self.paginate_queryset(feed_items)
        from interaction.serializers import FeedItemSerializer
        serializer = FeedItemSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

**Step 5: Update urls.py**

Update `app/interaction/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interaction import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('feed', views.FeedViewSet, basename='feed')

app_name = 'interaction'

urlpatterns = [
    path('', include(router.urls)),
]
```

**Step 6: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.FeedAPITests -v 2"
```

**Step 7: Commit**

```bash
git add app/interaction/serializers.py app/interaction/views.py app/interaction/urls.py app/interaction/tests/test_api.py
git commit -m "feat(interaction): add feed API endpoint"
```

---

## Phase 8: User Discovery

### Task 8.1: Add Discovery Endpoints

**Files:**
- Modify: `app/interaction/views.py`
- Test: `app/interaction/tests/test_api.py`

**Step 1: Write failing tests**

Add to `app/interaction/tests/test_api.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.DiscoveryAPITests -v 2"
```

**Step 3: Add discovery actions to UserViewSet**

Add to `app/interaction/views.py` UserViewSet:

```python
from django.db.models import Count

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by name or email."""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'results': []})

        users = get_user_model().objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        ).exclude(pk=request.user.pk if request.user.is_authenticated else None)[:20]

        serializer = UserSummarySerializer(users, many=True)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular users by follower count."""
        users = get_user_model().objects.annotate(
            follower_count=Count('followers_set')
        ).order_by('-follower_count')[:20]

        page = self.paginate_queryset(users)
        serializer = UserSummarySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def suggested(self, request):
        """Get suggested users based on who you follow."""
        # Get users followed by people you follow
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

        suggested_ids = Follow.objects.filter(
            follower_id__in=following_ids
        ).exclude(
            following=request.user
        ).exclude(
            following_id__in=following_ids
        ).values_list('following_id', flat=True).distinct()[:20]

        users = get_user_model().objects.filter(pk__in=suggested_ids)
        serializer = UserSummarySerializer(users, many=True)
        return Response({'results': serializer.data})
```

**Step 4: Run tests**

```bash
docker-compose run --rm app sh -c "python manage.py test interaction.tests.test_api.DiscoveryAPITests -v 2"
```

**Step 5: Commit**

```bash
git add app/interaction/views.py app/interaction/tests/test_api.py
git commit -m "feat(interaction): add user discovery endpoints"
```

---

## Phase 9: Run All Tests

### Task 9.1: Verify All Tests Pass

**Step 1: Run all tests**

```bash
docker-compose run --rm app sh -c "python manage.py test -v 2"
```

**Step 2: Fix any failing tests**

Review output and fix any issues.

**Step 3: Commit if needed**

```bash
git add .
git commit -m "fix: address test failures"
```

---

## Summary

This plan covers the backend implementation of social features:

1. **Phase 1**: Core models (Follow, FollowRequest, Block, Mute, User extensions)
2. **Phase 2**: Notification and preference models
3. **Phase 3**: Badge models
4. **Phase 4**: Follow API endpoints
5. **Phase 5**: Block/Mute API endpoints
6. **Phase 6**: Notification API endpoints
7. **Phase 7**: Activity feed service and API
8. **Phase 8**: User discovery endpoints
9. **Phase 9**: Integration testing

Frontend implementation will be covered in a separate plan after backend is complete.
