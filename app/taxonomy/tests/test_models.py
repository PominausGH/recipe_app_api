from django.test import TestCase
from taxonomy.models import Category, Tag


class CategoryModelTests(TestCase):
    """Tests for Category model."""

    def test_create_category(self):
        """Test creating a category is successful."""
        category = Category.objects.create(
            name='Breakfast',
            slug='breakfast',
        )

        self.assertEqual(str(category), 'Breakfast')

    def test_category_hierarchy(self):
        """Test category parent-child relationship."""
        parent = Category.objects.create(name='Main Dishes', slug='main-dishes')
        child = Category.objects.create(
            name='Pasta',
            slug='pasta',
            parent=parent,
        )

        self.assertEqual(child.parent, parent)


class TagModelTests(TestCase):
    """Tests for Tag model."""

    def test_create_tag(self):
        """Test creating a tag is successful."""
        tag = Tag.objects.create(
            name='Vegetarian',
            slug='vegetarian',
        )

        self.assertEqual(str(tag), 'Vegetarian')
