"""Tests for URL recipe import functionality."""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def create_user(**params):
    """Create and return a test user."""
    defaults = {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class ImportRecipeFromURLTests(TestCase):
    """Tests for POST /api/recipes/import-url/."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.url = reverse("recipe:recipe-import-url")

    def test_import_requires_authentication(self):
        """Test that unauthenticated users cannot import recipes."""
        self.client.force_authenticate(user=None)
        res = self.client.post(self.url, {"url": "https://example.com/recipe"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_import_requires_url(self):
        """Test that URL is required."""
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("url", res.data)

    def test_import_validates_url_format(self):
        """Test that invalid URLs are rejected."""
        res = self.client.post(self.url, {"url": "not-a-valid-url"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("recipe.views.scrape_me")
    def test_import_successful_recipe(self, mock_scrape):
        """Test successful recipe import from URL."""
        mock_scrape.return_value = MagicMock(
            title=lambda: "Chocolate Cake",
            description=lambda: "A delicious chocolate cake",
            total_time=lambda: 60,
            prep_time=lambda: 20,
            cook_time=lambda: 40,
            yields=lambda: "8 servings",
            instructions=lambda: "1. Mix ingredients\n2. Bake\n3. Enjoy",
            ingredients=lambda: ["2 cups flour", "1 cup sugar", "3 eggs"],
        )

        res = self.client.post(
            self.url, {"url": "https://www.allrecipes.com/recipe/123/chocolate-cake"}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Chocolate Cake")
        self.assertEqual(res.data["description"], "A delicious chocolate cake")
        self.assertIn("id", res.data)

    @patch("recipe.views.scrape_me")
    def test_import_creates_recipe_as_draft(self, mock_scrape):
        """Test that imported recipes are created as drafts."""
        mock_scrape.return_value = MagicMock(
            title=lambda: "Test Recipe",
            description=lambda: "Test description",
            total_time=lambda: 30,
            prep_time=lambda: 10,
            cook_time=lambda: 20,
            yields=lambda: "4 servings",
            instructions=lambda: "Test instructions",
            ingredients=lambda: ["ingredient 1", "ingredient 2"],
        )

        res = self.client.post(
            self.url, {"url": "https://www.allrecipes.com/recipe/123/test"}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertFalse(res.data["is_published"])

    @patch("recipe.views.scrape_me")
    def test_import_sets_current_user_as_author(self, mock_scrape):
        """Test that imported recipe has current user as author."""
        mock_scrape.return_value = MagicMock(
            title=lambda: "Test Recipe",
            description=lambda: "Test description",
            total_time=lambda: 30,
            prep_time=lambda: 10,
            cook_time=lambda: 20,
            yields=lambda: "4 servings",
            instructions=lambda: "Test instructions",
            ingredients=lambda: ["ingredient 1"],
        )

        res = self.client.post(
            self.url, {"url": "https://www.allrecipes.com/recipe/123/test"}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["author"], self.user.id)

    @patch("recipe.views.scrape_me")
    def test_import_handles_unsupported_site(self, mock_scrape):
        """Test handling of unsupported recipe sites."""
        from recipe_scrapers._exceptions import WebsiteNotImplementedError

        mock_scrape.side_effect = WebsiteNotImplementedError("example.com")

        res = self.client.post(self.url, {"url": "https://example.com/recipe"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    @patch("recipe.views.scrape_me")
    def test_import_handles_scraping_error(self, mock_scrape):
        """Test handling of general scraping errors."""
        mock_scrape.side_effect = Exception("Failed to fetch page")

        res = self.client.post(
            self.url, {"url": "https://www.allrecipes.com/recipe/123/test"}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    @patch("recipe.views.scrape_me")
    def test_import_handles_missing_fields(self, mock_scrape):
        """Test import when some fields are missing from source."""
        mock_scrape.return_value = MagicMock(
            title=lambda: "Simple Recipe",
            description=lambda: None,
            total_time=lambda: None,
            prep_time=lambda: None,
            cook_time=lambda: None,
            yields=lambda: None,
            instructions=lambda: "Just cook it",
            ingredients=lambda: ["stuff"],
        )

        res = self.client.post(
            self.url, {"url": "https://www.allrecipes.com/recipe/123/simple"}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Simple Recipe")
        self.assertEqual(res.data["description"], "")

    @patch("recipe.views.scrape_me")
    def test_import_parses_servings_from_yields(self, mock_scrape):
        """Test that servings are parsed from yields string."""
        mock_scrape.return_value = MagicMock(
            title=lambda: "Test Recipe",
            description=lambda: "Test",
            total_time=lambda: 30,
            prep_time=lambda: 10,
            cook_time=lambda: 20,
            yields=lambda: "6 servings",
            instructions=lambda: "Instructions",
            ingredients=lambda: ["ingredient"],
        )

        res = self.client.post(
            self.url, {"url": "https://www.allrecipes.com/recipe/123/test"}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["servings"], 6)

    @patch("recipe.views.scrape_me")
    def test_import_stores_source_url(self, mock_scrape):
        """Test that source URL is stored with the recipe."""
        mock_scrape.return_value = MagicMock(
            title=lambda: "Test Recipe",
            description=lambda: "Test",
            total_time=lambda: 30,
            prep_time=lambda: 10,
            cook_time=lambda: 20,
            yields=lambda: "4 servings",
            instructions=lambda: "Instructions",
            ingredients=lambda: ["ingredient"],
        )

        source_url = "https://www.allrecipes.com/recipe/123/test"
        res = self.client.post(self.url, {"url": source_url})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["source_url"], source_url)
