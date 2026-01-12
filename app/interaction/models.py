from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


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
