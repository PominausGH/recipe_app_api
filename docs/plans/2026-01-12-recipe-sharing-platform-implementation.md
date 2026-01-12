# Recipe Sharing Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a full-featured recipe sharing platform with user accounts, recipes, ratings, favorites, and comments.

**Architecture:** Django REST Framework API with JWT authentication. PostgreSQL database via Docker. Modular apps: core (users), taxonomy (categories/tags), recipe (recipes/ingredients), interaction (ratings/favorites/comments).

**Tech Stack:** Django 3.2, DRF, djangorestframework-simplejwt, django-filter, Pillow, PostgreSQL

---

## Phase 1: Project Setup & Dependencies

### Task 1.1: Update Dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `requirements.dev.txt`

**Step 1: Update requirements.txt**

```
Django>=3.2.4,<3.3
djangorestframework>=3.12.4,<3.13
djangorestframework-simplejwt>=5.0.0,<6.0
django-filter>=21.1,<22.0
Pillow>=9.0.0,<10.0
psycopg2>=2.8.6,<=2.9
```

**Step 2: Update requirements.dev.txt**

```
flake8>=3.9.2,<4.0
pytest>=7.0.0,<8.0
pytest-django>=4.5.0,<5.0
factory-boy>=3.2.0,<4.0
```

**Step 3: Commit**

```bash
git add requirements.txt requirements.dev.txt
git commit -m "chore: update dependencies for recipe platform"
```

---

### Task 1.2: Create Settings Structure

**Files:**
- Create: `app/app/settings/__init__.py`
- Create: `app/app/settings/base.py`
- Create: `app/app/settings/dev.py`
- Modify: `app/app/settings.py` (delete after migration)

**Step 1: Create settings directory and __init__.py**

Create `app/app/settings/__init__.py`:
```python
from .dev import *
```

**Step 2: Create base.py with shared settings**

Create `app/app/settings/base.py`:
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'django_filters',
    # Local apps
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

**Step 3: Create dev.py**

Create `app/app/settings/dev.py`:
```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST', 'db'),
        'NAME': os.environ.get('DB_NAME', 'devdb'),
        'USER': os.environ.get('DB_USER', 'devuser'),
        'PASSWORD': os.environ.get('DB_PASS', 'password'),
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Step 4: Delete old settings.py and commit**

```bash
rm app/app/settings.py
git add app/app/settings/
git commit -m "refactor: split settings into base/dev modules"
```

---

## Phase 2: Custom User Model

### Task 2.1: Write User Model Test

**Files:**
- Create: `app/core/tests/test_models.py`

**Step 1: Write the failing test**

Create `app/core/tests/test_models.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):
    """Tests for custom User model."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'admin@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_profile_fields(self):
        """Test user has profile fields."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
            bio='Test bio',
        )

        self.assertEqual(user.bio, 'Test bio')
```

**Step 2: Run test to verify it fails**

Run: `docker-compose run --rm app sh -c "python manage.py test core.tests.test_models"`
Expected: FAIL (User model not implemented)

**Step 3: Commit test**

```bash
git add app/core/tests/test_models.py
git commit -m "test: add User model tests"
```

---

### Task 2.2: Implement User Model

**Files:**
- Modify: `app/core/models.py`

**Step 1: Implement User model**

Replace `app/core/models.py`:
```python
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
```

**Step 2: Run tests to verify they pass**

Run: `docker-compose run --rm app sh -c "python manage.py test core.tests.test_models"`
Expected: PASS (5 tests)

**Step 3: Make migrations and commit**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations"
git add app/core/
git commit -m "feat: implement custom User model with email auth"
```

---

## Phase 3: Taxonomy App (Categories & Tags)

### Task 3.1: Create Taxonomy App

**Files:**
- Create: `app/taxonomy/__init__.py`
- Create: `app/taxonomy/apps.py`
- Create: `app/taxonomy/models.py`
- Create: `app/taxonomy/admin.py`
- Create: `app/taxonomy/tests/__init__.py`
- Modify: `app/app/settings/base.py` (add to INSTALLED_APPS)

**Step 1: Create app structure**

```bash
mkdir -p app/taxonomy/tests
touch app/taxonomy/__init__.py
touch app/taxonomy/tests/__init__.py
```

**Step 2: Create apps.py**

Create `app/taxonomy/apps.py`:
```python
from django.apps import AppConfig


class TaxonomyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taxonomy'
```

**Step 3: Add to INSTALLED_APPS in base.py**

Add `'taxonomy',` after `'core',` in INSTALLED_APPS.

**Step 4: Commit**

```bash
git add app/taxonomy/ app/app/settings/base.py
git commit -m "chore: create taxonomy app structure"
```

---

### Task 3.2: Write Category Model Test

**Files:**
- Create: `app/taxonomy/tests/test_models.py`

**Step 1: Write the failing test**

Create `app/taxonomy/tests/test_models.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run: `docker-compose run --rm app sh -c "python manage.py test taxonomy.tests.test_models"`
Expected: FAIL (models not defined)

**Step 3: Commit test**

```bash
git add app/taxonomy/tests/test_models.py
git commit -m "test: add Category and Tag model tests"
```

---

### Task 3.3: Implement Category and Tag Models

**Files:**
- Modify: `app/taxonomy/models.py`

**Step 1: Implement models**

Create `app/taxonomy/models.py`:
```python
from django.db import models


class Category(models.Model):
    """Category for recipes (hierarchical)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag for recipes (flat)."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
```

**Step 2: Run tests to verify they pass**

Run: `docker-compose run --rm app sh -c "python manage.py test taxonomy.tests.test_models"`
Expected: PASS (3 tests)

**Step 3: Make migrations and commit**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations taxonomy"
git add app/taxonomy/
git commit -m "feat: implement Category and Tag models"
```

---

## Phase 4: Recipe App - Models

### Task 4.1: Create Recipe App Structure

**Files:**
- Create: `app/recipe/__init__.py`
- Create: `app/recipe/apps.py`
- Create: `app/recipe/models.py`
- Create: `app/recipe/tests/__init__.py`
- Modify: `app/app/settings/base.py`

**Step 1: Create app structure**

```bash
mkdir -p app/recipe/tests
touch app/recipe/__init__.py
touch app/recipe/tests/__init__.py
```

**Step 2: Create apps.py**

Create `app/recipe/apps.py`:
```python
from django.apps import AppConfig


class RecipeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe'
```

**Step 3: Add to INSTALLED_APPS**

Add `'recipe',` after `'taxonomy',` in INSTALLED_APPS.

**Step 4: Commit**

```bash
git add app/recipe/ app/app/settings/base.py
git commit -m "chore: create recipe app structure"
```

---

### Task 4.2: Write Recipe Model Tests

**Files:**
- Create: `app/recipe/tests/test_models.py`

**Step 1: Write the failing test**

Create `app/recipe/tests/test_models.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Recipe, Ingredient
from taxonomy.models import Category, Tag


class RecipeModelTests(TestCase):
    """Tests for Recipe model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            description='Test description',
            instructions='Test instructions',
            prep_time=10,
            cook_time=20,
            servings=4,
            difficulty='easy',
        )

        self.assertEqual(str(recipe), 'Test Recipe')
        self.assertEqual(recipe.author, self.user)

    def test_recipe_with_category(self):
        """Test recipe can have a category."""
        category = Category.objects.create(name='Dinner', slug='dinner')
        recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            instructions='Test',
            category=category,
        )

        self.assertEqual(recipe.category, category)

    def test_recipe_with_tags(self):
        """Test recipe can have multiple tags."""
        tag1 = Tag.objects.create(name='Vegan', slug='vegan')
        tag2 = Tag.objects.create(name='Quick', slug='quick')
        recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            instructions='Test',
        )
        recipe.tags.add(tag1, tag2)

        self.assertEqual(recipe.tags.count(), 2)


class IngredientModelTests(TestCase):
    """Tests for Ingredient model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Test Recipe',
            instructions='Test',
        )

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        ingredient = Ingredient.objects.create(
            recipe=self.recipe,
            name='Flour',
            quantity=2.5,
            unit='cups',
            order=1,
        )

        self.assertEqual(str(ingredient), 'Flour')

    def test_ingredient_cascade_delete(self):
        """Test ingredients deleted when recipe deleted."""
        Ingredient.objects.create(
            recipe=self.recipe,
            name='Sugar',
            quantity=1,
            unit='cups',
            order=1,
        )

        self.recipe.delete()
        self.assertEqual(Ingredient.objects.count(), 0)
```

**Step 2: Run test to verify it fails**

Run: `docker-compose run --rm app sh -c "python manage.py test recipe.tests.test_models"`
Expected: FAIL (models not defined)

**Step 3: Commit test**

```bash
git add app/recipe/tests/test_models.py
git commit -m "test: add Recipe and Ingredient model tests"
```

---

### Task 4.3: Implement Recipe and Ingredient Models

**Files:**
- Modify: `app/recipe/models.py`

**Step 1: Implement models**

Create `app/recipe/models.py`:
```python
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Recipe(models.Model):
    """Recipe model."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
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
        default='medium',
    )
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    category = models.ForeignKey(
        'taxonomy.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        'taxonomy.Tag',
        blank=True,
        related_name='recipes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_time(self):
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook


class Ingredient(models.Model):
    """Ingredient for a recipe."""
    UNIT_CHOICES = [
        ('cups', 'Cups'),
        ('tbsp', 'Tablespoons'),
        ('tsp', 'Teaspoons'),
        ('oz', 'Ounces'),
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('pieces', 'Pieces'),
        ('pinch', 'Pinch'),
        ('to taste', 'To taste'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
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
        ordering = ['order']

    def __str__(self):
        return self.name
```

**Step 2: Run tests to verify they pass**

Run: `docker-compose run --rm app sh -c "python manage.py test recipe.tests.test_models"`
Expected: PASS (5 tests)

**Step 3: Make migrations and commit**

```bash
docker-compose run --rm app sh -c "python manage.py makemigrations recipe"
git add app/recipe/
git commit -m "feat: implement Recipe and Ingredient models"
```

---

## Phase 5: Recipe API

### Task 5.1: Create Permissions

**Files:**
- Create: `app/recipe/permissions.py`

**Step 1: Create permissions**

Create `app/recipe/permissions.py`:
```python
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow only owners to modify objects."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
```

**Step 2: Commit**

```bash
git add app/recipe/permissions.py
git commit -m "feat: add IsOwnerOrReadOnly permission"
```

---

### Task 5.2: Write Recipe API Tests

**Files:**
- Create: `app/recipe/tests/test_api.py`

**Step 1: Write the failing tests**

Create `app/recipe/tests/test_api.py`:
```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from recipe.models import Recipe


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()

    def test_list_published_recipes(self):
        """Test listing published recipes."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
        )
        Recipe.objects.create(
            author=user,
            title='Published Recipe',
            instructions='Test',
            is_published=True,
        )
        Recipe.objects.create(
            author=user,
            title='Draft Recipe',
            instructions='Test',
            is_published=False,
        )

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_create_recipe_requires_auth(self):
        """Test creating recipe requires authentication."""
        payload = {'title': 'Test', 'instructions': 'Test'}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Test Recipe',
            'instructions': 'Test instructions',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 4,
            'difficulty': 'easy',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.author, self.user)

    def test_update_own_recipe(self):
        """Test updating own recipe."""
        recipe = Recipe.objects.create(
            author=self.user,
            title='Original',
            instructions='Test',
        )

        res = self.client.patch(detail_url(recipe.id), {'title': 'Updated'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'Updated')

    def test_cannot_update_other_users_recipe(self):
        """Test cannot update another user's recipe."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='test123',
        )
        recipe = Recipe.objects.create(
            author=other_user,
            title='Other Recipe',
            instructions='Test',
            is_published=True,
        )

        res = self.client.patch(detail_url(recipe.id), {'title': 'Hacked'})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
```

**Step 2: Run test to verify it fails**

Run: `docker-compose run --rm app sh -c "python manage.py test recipe.tests.test_api"`
Expected: FAIL (URL not defined)

**Step 3: Commit test**

```bash
git add app/recipe/tests/test_api.py
git commit -m "test: add Recipe API tests"
```

---

### Task 5.3: Implement Recipe Serializers

**Files:**
- Create: `app/recipe/serializers.py`

**Step 1: Create serializers**

Create `app/recipe/serializers.py`:
```python
from rest_framework import serializers
from recipe.models import Recipe, Ingredient
from taxonomy.models import Category, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'unit', 'order']


class RecipeListSerializer(serializers.ModelSerializer):
    """Serializer for recipe list view."""
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'author', 'author_name',
            'prep_time', 'cook_time', 'total_time', 'servings',
            'difficulty', 'image', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'created_at']


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for recipe detail view."""
    ingredients = IngredientSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'author',
            'author_name', 'prep_time', 'cook_time', 'total_time',
            'servings', 'difficulty', 'image', 'is_published',
            'category', 'tags', 'ingredients', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating recipes."""
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions',
            'prep_time', 'cook_time', 'servings', 'difficulty',
            'is_published', 'category', 'tags', 'ingredients',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for idx, ingredient_data in enumerate(ingredients_data):
            ingredient_data['order'] = idx
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for idx, ingredient_data in enumerate(ingredients_data):
                ingredient_data['order'] = idx
                Ingredient.objects.create(recipe=instance, **ingredient_data)

        return instance
```

**Step 2: Commit**

```bash
git add app/recipe/serializers.py
git commit -m "feat: add Recipe serializers"
```

---

### Task 5.4: Implement Recipe Views and URLs

**Files:**
- Create: `app/recipe/views.py`
- Create: `app/recipe/urls.py`
- Modify: `app/app/urls.py`

**Step 1: Create views**

Create `app/recipe/views.py`:
```python
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from recipe.models import Recipe
from recipe.serializers import (
    RecipeListSerializer,
    RecipeDetailSerializer,
    RecipeCreateSerializer,
)
from recipe.permissions import IsOwnerOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipes."""
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return recipes based on user authentication."""
        if self.request.user.is_authenticated:
            # Show user's own recipes (including drafts) + published
            return Recipe.objects.filter(
                models.Q(author=self.request.user) |
                models.Q(is_published=True)
            ).distinct()
        return Recipe.objects.filter(is_published=True)

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return RecipeListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(author=self.request.user)


# Fix import at top
from django.db import models
```

**Step 2: Create urls.py**

Create `app/recipe/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipe')

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
```

**Step 3: Update main urls.py**

Replace `app/app/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipe.urls')),
]
```

**Step 4: Run tests to verify they pass**

Run: `docker-compose run --rm app sh -c "python manage.py test recipe.tests.test_api"`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add app/recipe/views.py app/recipe/urls.py app/app/urls.py
git commit -m "feat: implement Recipe API ViewSet and URLs"
```

---

## Phase 6: Run All Tests

### Task 6.1: Run Full Test Suite

**Step 1: Run all tests**

Run: `docker-compose run --rm app sh -c "python manage.py test"`
Expected: All tests pass

**Step 2: Commit any fixes if needed**

---

## Next Phases (Summary)

The following phases continue the same TDD pattern:

- **Phase 7:** Interaction app (Rating, Favorite, Comment models + API)
- **Phase 8:** User authentication API (register, login, JWT, profile)
- **Phase 9:** Image upload handling with resize
- **Phase 10:** Filtering and search
- **Phase 11:** Rate limiting
- **Phase 12:** Integration tests

---

## Execution Checkpoint

After completing Phase 6, you have a working recipe CRUD API. Run:

```bash
docker-compose up
# Visit http://localhost:8000/api/recipes/
```

Continue with Phase 7+ or stop here for MVP.
