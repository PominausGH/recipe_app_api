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