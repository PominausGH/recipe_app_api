from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Recipe(models.Model):
    """Recipe model."""

    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    instructions = models.TextField(max_length=10000)
    prep_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1440)],
    )
    cook_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1440)],
    )
    servings = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="medium",
    )
    image = models.ImageField(upload_to="recipes/", null=True, blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    is_published = models.BooleanField(default=False)
    category = models.ForeignKey(
        "taxonomy.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        "taxonomy.Tag",
        blank=True,
        related_name="recipes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def total_time(self):
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook

    @property
    def average_rating(self):
        """Calculate average rating for this recipe."""
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return None

    @property
    def rating_count(self):
        """Get the number of ratings for this recipe."""
        return self.ratings.count()


class Ingredient(models.Model):
    """Ingredient for a recipe."""

    UNIT_CHOICES = [
        ("cups", "Cups"),
        ("tbsp", "Tablespoons"),
        ("tsp", "Teaspoons"),
        ("oz", "Ounces"),
        ("g", "Grams"),
        ("kg", "Kilograms"),
        ("ml", "Milliliters"),
        ("l", "Liters"),
        ("pieces", "Pieces"),
        ("pinch", "Pinch"),
        ("to taste", "To taste"),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name
