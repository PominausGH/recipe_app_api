from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.models import Recipe
from rest_framework import status
from rest_framework.test import APIClient
from taxonomy.models import Category, Tag


class FullUserJourneyTest(TestCase):
    """
    End-to-end test simulating a complete user journey through the platform.

    Scenario: A new user registers, browses recipes, creates their own,
    interacts with other recipes, and manages their content.
    """

    def setUp(self):
        self.client = APIClient()

        # Set up some existing content
        self.existing_chef = get_user_model().objects.create_user(
            email="existingchef@example.com",
            password="testpass123",
            name="Existing Chef",
        )
        self.category = Category.objects.create(name="Desserts", slug="desserts")
        self.tag_easy = Tag.objects.create(name="Easy", slug="easy")
        self.tag_quick = Tag.objects.create(name="Quick", slug="quick")

        self.existing_recipe = Recipe.objects.create(
            author=self.existing_chef,
            title="Chocolate Cake",
            description="Rich chocolate cake",
            instructions="Mix ingredients and bake at 350F for 30 minutes",
            category=self.category,
            prep_time=20,
            cook_time=30,
            servings=8,
            difficulty="medium",
            is_published=True,
        )
        self.existing_recipe.tags.add(self.tag_easy)

    def test_complete_user_journey(self):
        """Test a complete user journey through the platform."""

        # ========================================
        # PHASE 1: Discovery (Anonymous Browsing)
        # ========================================

        recipes_url = reverse("recipe:recipe-list")

        # Browse recipes without logging in
        res = self.client.get(recipes_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "Chocolate Cake")

        # Search for recipes
        res = self.client.get(recipes_url, {"search": "chocolate"})
        self.assertEqual(len(res.data["results"]), 1)

        # Filter by category
        res = self.client.get(recipes_url, {"category": self.category.id})
        self.assertEqual(len(res.data["results"]), 1)

        # View recipe detail
        detail_url = reverse("recipe:recipe-detail", args=[self.existing_recipe.id])
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Chocolate Cake")

        # Read comments (empty for now)
        comments_url = reverse("recipe:recipe-comments", args=[self.existing_recipe.id])
        res = self.client.get(comments_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

        # ========================================
        # PHASE 2: Registration & Authentication
        # ========================================

        # Register a new account
        register_url = reverse("auth:register")
        res = self.client.post(
            register_url,
            {
                "email": "newchef@example.com",
                "password": "securefoodpass123",
                "password_confirm": "securefoodpass123",
                "name": "New Chef",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Login
        login_url = reverse("auth:login")
        res = self.client.post(
            login_url,
            {
                "email": "newchef@example.com",
                "password": "securefoodpass123",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # ========================================
        # PHASE 3: Interaction with Existing Content
        # ========================================

        # Rate the existing recipe
        rate_url = reverse("recipe:recipe-rate", args=[self.existing_recipe.id])
        res = self.client.post(
            rate_url,
            {
                "score": 5,
                "review": "Absolutely delicious! Made it for my family.",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Add to favorites
        favorite_url = reverse("recipe:recipe-favorite", args=[self.existing_recipe.id])
        res = self.client.post(favorite_url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Leave a comment
        res = self.client.post(
            comments_url,
            {
                "text": "Can I substitute dark chocolate for milk chocolate?",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comment_id = res.data["id"]

        # Verify comment appears
        res = self.client.get(comments_url)
        self.assertEqual(len(res.data), 1)

        # ========================================
        # PHASE 4: Content Creation
        # ========================================

        # Create a new recipe (draft first)
        res = self.client.post(
            recipes_url,
            {
                "title": "My Famous Cookies",
                "description": "Crispy on the outside, chewy on the inside",
                "instructions": (
                    "1. Mix butter and sugar\n2. Add flour\n3. Bake at 375F"
                ),
                "prep_time": 15,
                "cook_time": 12,
                "servings": 24,
                "difficulty": "easy",
                "category": self.category.id,
                "is_published": False,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        my_recipe_id = res.data["id"]
        my_recipe_url = reverse("recipe:recipe-detail", args=[my_recipe_id])

        # Update to add tags and publish
        res = self.client.patch(
            my_recipe_url,
            {
                "tags": [self.tag_easy.id, self.tag_quick.id],
                "is_published": True,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify recipe is now public
        self.client.credentials()  # Clear auth
        res = self.client.get(recipes_url)
        self.assertEqual(len(res.data["results"]), 2)  # Now 2 public recipes

        # ========================================
        # PHASE 5: Receiving Interaction
        # ========================================

        # Another user interacts with our recipe
        self.client.force_authenticate(user=self.existing_chef)

        # Rate the new recipe
        new_recipe_rate_url = reverse("recipe:recipe-rate", args=[my_recipe_id])
        res = self.client.post(
            new_recipe_rate_url,
            {
                "score": 4,
                "review": "Nice recipe!",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Reply to comment on their recipe
        res = self.client.post(
            comments_url,
            {
                "text": "Yes, dark chocolate works great!",
                "parent": comment_id,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # ========================================
        # PHASE 6: Verify Final State
        # ========================================

        # Check recipe has rating
        res = self.client.get(my_recipe_url)
        self.assertEqual(res.data["average_rating"], 4.0)
        self.assertEqual(res.data["rating_count"], 1)

        # Check comment thread
        res = self.client.get(comments_url)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(len(res.data[0]["replies"]), 1)

        # Verify search finds both recipes
        res = self.client.get(recipes_url, {"search": "chocolate"})
        self.assertGreaterEqual(len(res.data["results"]), 1)

        # Filter by tag
        res = self.client.get(recipes_url, {"tags": self.tag_easy.id})
        self.assertEqual(len(res.data["results"]), 2)  # Both have 'easy' tag

        # Order by rating
        res = self.client.get(recipes_url, {"ordering": "-avg_rating"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        print("Full user journey test completed successfully!")
