from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe
from taxonomy.models import Category, Tag


class RecipeCRUDIntegrationTests(TestCase):
    """Integration tests for recipe CRUD operations."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="chef@example.com",
            password="testpass123",
            name="Test Chef",
        )
        self.category = Category.objects.create(name="Dinner", slug="dinner")
        self.tag = Tag.objects.create(name="Healthy", slug="healthy")

    def test_full_recipe_lifecycle(self):
        """Test complete recipe create, read, update, delete flow."""
        # Step 1: Login
        login_url = reverse("auth:login")
        res = self.client.post(
            login_url,
            {
                "email": "chef@example.com",
                "password": "testpass123",
            },
        )
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Step 2: Create a recipe
        recipes_url = reverse("recipe:recipe-list")
        recipe_payload = {
            "title": "Grilled Salmon",
            "description": "Delicious grilled salmon with herbs",
            "instructions": "1. Season salmon\n2. Grill 10 min\n3. Serve",
            "prep_time": 15,
            "cook_time": 10,
            "servings": 2,
            "difficulty": "medium",
            "category": self.category.id,
            "is_published": False,
        }

        res = self.client.post(recipes_url, recipe_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe_id = res.data["id"]

        # Verify recipe is in database
        recipe = Recipe.objects.get(id=recipe_id)
        self.assertEqual(recipe.title, "Grilled Salmon")
        self.assertEqual(recipe.author, self.user)
        self.assertFalse(recipe.is_published)

        # Step 3: Get recipe detail
        detail_url = reverse("recipe:recipe-detail", args=[recipe_id])
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Grilled Salmon")

        # Step 4: Update recipe (publish it)
        res = self.client.patch(
            detail_url,
            {
                "is_published": True,
                "title": "Perfect Grilled Salmon",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertTrue(recipe.is_published)
        self.assertEqual(recipe.title, "Perfect Grilled Salmon")

        # Step 5: Add tags
        res = self.client.patch(
            detail_url,
            {
                "tags": [self.tag.id],
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertIn(self.tag, recipe.tags.all())

        # Step 6: Verify recipe appears in public list
        self.client.credentials()  # Clear auth (anonymous)
        res = self.client.get(recipes_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe_titles = [r["title"] for r in res.data["results"]]
        self.assertIn("Perfect Grilled Salmon", recipe_titles)

        # Step 7: Delete recipe (re-authenticate)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        res = self.client.delete(detail_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Verify recipe is deleted
        self.assertFalse(Recipe.objects.filter(id=recipe_id).exists())

    def test_draft_recipe_visibility(self):
        """Test that draft recipes are only visible to owner."""
        # Create draft recipe
        Recipe.objects.create(
            author=self.user,
            title="Draft Recipe",
            instructions="Secret recipe",
            is_published=False,
        )

        recipes_url = reverse("recipe:recipe-list")

        # Anonymous user should not see draft
        res = self.client.get(recipes_url)
        self.assertEqual(len(res.data["results"]), 0)

        # Owner should see their draft
        self.client.force_authenticate(user=self.user)
        res = self.client.get(recipes_url)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "Draft Recipe")

        # Other user should not see draft
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=other_user)
        res = self.client.get(recipes_url)
        self.assertEqual(len(res.data["results"]), 0)

    def test_cannot_modify_other_users_recipe(self):
        """Test that users cannot modify other users' recipes."""
        # Create recipe owned by self.user
        recipe = Recipe.objects.create(
            author=self.user,
            title="My Recipe",
            instructions="Test",
            is_published=True,
        )

        # Login as different user
        other_user = get_user_model().objects.create_user(
            email="hacker@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=other_user)

        detail_url = reverse("recipe:recipe-detail", args=[recipe.id])

        # Try to update
        res = self.client.patch(detail_url, {"title": "Hacked!"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Try to delete
        res = self.client.delete(detail_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Verify recipe unchanged
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, "My Recipe")
