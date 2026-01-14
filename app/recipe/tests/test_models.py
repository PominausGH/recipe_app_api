from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Recipe, Ingredient
from taxonomy.models import Category, Tag


class RecipeModelTests(TestCase):
    """Tests for Recipe model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            description="Test description",
            instructions="Test instructions",
            prep_time=10,
            cook_time=20,
            servings=4,
            difficulty="easy",
        )

        self.assertEqual(str(recipe), "Test Recipe")
        self.assertEqual(recipe.author, self.user)

    def test_recipe_with_category(self):
        """Test recipe can have a category."""
        category = Category.objects.create(name="Dinner", slug="dinner")
        recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            instructions="Test",
            category=category,
        )

        self.assertEqual(recipe.category, category)

    def test_recipe_with_tags(self):
        """Test recipe can have multiple tags."""
        tag1 = Tag.objects.create(name="Vegan", slug="vegan")
        tag2 = Tag.objects.create(name="Quick", slug="quick")
        recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            instructions="Test",
        )
        recipe.tags.add(tag1, tag2)

        self.assertEqual(recipe.tags.count(), 2)


class IngredientModelTests(TestCase):
    """Tests for Ingredient model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Test Recipe",
            instructions="Test",
        )

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        ingredient = Ingredient.objects.create(
            recipe=self.recipe,
            name="Flour",
            quantity=2.5,
            unit="cups",
            order=1,
        )

        self.assertEqual(str(ingredient), "Flour")

    def test_ingredient_cascade_delete(self):
        """Test ingredients deleted when recipe deleted."""
        Ingredient.objects.create(
            recipe=self.recipe,
            name="Sugar",
            quantity=1,
            unit="cups",
            order=1,
        )

        self.recipe.delete()
        self.assertEqual(Ingredient.objects.count(), 0)
