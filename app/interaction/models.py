from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Rating(models.Model):
    """Rating for a recipe (1-5 stars with optional review)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    recipe = models.ForeignKey(
        'recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} rated {self.recipe.title}: {self.score}'


class Favorite(models.Model):
    """User's favorite recipe."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        'recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} favorited {self.recipe.title}'


class Comment(models.Model):
    """Comment on a recipe (supports nested replies)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    recipe = models.ForeignKey(
        'recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(max_length=2000)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.email} on {self.recipe.title}'


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
        actor_str = self.actor.email if self.actor else 'System'
        return f'{actor_str} {self.verb} {self.recipient.email}'


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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


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