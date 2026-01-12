# Recipe Sharing Platform - Design Document

**Date:** 2026-01-12
**Status:** Approved

## Overview

A recipe sharing platform where users create accounts and share recipes publicly. Full-featured with photos, categories, ratings, reviews, favorites, and comments.

## Tech Stack

- **Framework:** Django 3.2+
- **API:** Django REST Framework
- **Auth:** JWT (simplejwt) + Social auth (django-allauth)
- **Storage:** Local (dev) / AWS S3 (prod) via django-storages
- **Database:** PostgreSQL (via Docker)

## Data Models

### User Model (extends AbstractUser)
- Email as username
- Profile photo, bio
- Date joined

### Recipe Model
| Field | Type | Notes |
|-------|------|-------|
| author | FK(User) | CASCADE delete |
| title | CharField(200) | Required, 3-200 chars |
| description | TextField | Max 2000 chars |
| instructions | TextField | Required, max 10000 chars |
| prep_time | PositiveIntegerField | Minutes, max 1440 |
| cook_time | PositiveIntegerField | Minutes, max 1440 |
| servings | PositiveIntegerField | 1-100 |
| difficulty | CharField | easy/medium/hard |
| image | ImageField | Max 5MB, jpeg/png/webp |
| is_published | BooleanField | Draft vs public |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |

### Ingredient Model
| Field | Type | Notes |
|-------|------|-------|
| recipe | FK(Recipe) | CASCADE delete |
| name | CharField(100) | Required |
| quantity | DecimalField | Positive, max 10000 |
| unit | CharField | Predefined choices |
| order | PositiveIntegerField | Display sequence |

### Category Model
- name, slug
- parent (self FK for hierarchy)

### Tag Model
- name, slug
- Many-to-many with Recipe

### Rating Model
| Field | Type | Notes |
|-------|------|-------|
| user | FK(User) | |
| recipe | FK(Recipe) | |
| score | PositiveIntegerField | 1-5 |
| review | TextField | Optional |
| created_at | DateTimeField | |

Unique constraint: (user, recipe)

### Favorite Model
- user, recipe (many-to-many through)
- created_at

### Comment Model
| Field | Type | Notes |
|-------|------|-------|
| user | FK(User) | |
| recipe | FK(Recipe) | |
| text | TextField | Required |
| parent | FK(self) | For nested replies |
| created_at | DateTimeField | |

### NutritionInfo Model (OneToOne with Recipe)
- calories, protein, carbs, fat, fiber, sodium
- All per serving

## API Endpoints

### Authentication (`/api/auth/`)
```
POST /register/          - Email/password signup
POST /login/             - Get JWT tokens
POST /logout/            - Invalidate token
POST /refresh/           - Refresh access token
POST /social/{provider}/ - Google/Facebook auth
GET  /me/                - Current user profile
PATCH /me/               - Update profile
```

### Recipes (`/api/recipes/`)
```
GET    /                 - List (paginated, filterable)
POST   /                 - Create (authenticated)
GET    /{id}/            - Detail
PATCH  /{id}/            - Update (owner only)
DELETE /{id}/            - Delete (owner only)
POST   /{id}/image/      - Upload image
```

### Recipe Interactions
```
POST /recipes/{id}/rate/      - Add/update rating
POST /recipes/{id}/favorite/  - Toggle favorite
GET  /recipes/{id}/comments/  - List comments
POST /recipes/{id}/comments/  - Add comment
```

### Discovery
```
GET /categories/              - List categories
GET /tags/                    - List tags
GET /users/{id}/recipes/      - User's public recipes
GET /me/favorites/            - My favorited recipes
GET /me/recipes/              - My recipes (incl. drafts)
```

### Filtering & Search
Query parameters on recipe list:
- `?search=` - Full-text search (title, description)
- `?category=` - Filter by category
- `?tags=` - Filter by tags (comma-separated)
- `?difficulty=` - easy/medium/hard
- `?max_time=` - Max total time (prep + cook)
- `?ordering=` - rating, -created_at, popularity

## Project Structure

```
app/
├── app/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── dev.py          # Local storage
│   │   └── prod.py         # S3 storage
│   └── urls.py
├── core/                    # User model, admin
│   ├── models.py
│   └── admin.py
├── recipe/                  # Recipe functionality
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   ├── permissions.py
│   └── tests/
├── interaction/             # Ratings, favorites, comments
│   ├── models.py
│   ├── serializers.py
│   └── views.py
└── taxonomy/                # Categories & tags
    ├── models.py
    └── serializers.py
```

## Dependencies

```
djangorestframework
djangorestframework-simplejwt
django-allauth
dj-rest-auth
django-filter
django-storages
boto3
Pillow
```

## Authentication & Permissions

### JWT Tokens
- Access token: 15 min expiry
- Refresh token: 7 days expiry

### Permission Classes
- `IsOwnerOrReadOnly` - Anyone reads, owner modifies
- `IsAuthenticatedOrReadOnly` - Login to create
- `IsCommentOwnerOrRecipeOwner` - Comment deletion

### Access Rules
| Action | Permission |
|--------|-----------|
| View published recipes | Anyone |
| View drafts | Owner only |
| Create recipe | Authenticated |
| Edit/delete recipe | Owner only |
| Rate/favorite | Authenticated |
| Comment | Authenticated |
| Delete comment | Comment author or recipe owner |

### Rate Limiting
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Recipe creation: 20/day

## Validation Rules

### Recipe
- Title: 3-200 characters, required
- Description: max 2000 characters
- Instructions: required, max 10000 characters
- Prep/cook time: positive integers, max 1440 min
- Servings: 1-100
- At least 1 ingredient required
- Image: max 5MB, jpeg/png/webp

### Ingredient
- Name: required, max 100 chars
- Quantity: positive decimal, max 10000
- Unit: predefined choices

### Image Processing
- Resize on upload: max 1200px width
- Generate thumbnail: 300px
- Strip EXIF data

## Error Response Format

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "title": ["This field is required."],
    "ingredients": ["At least one ingredient required."]
  }
}
```

## Testing Strategy

### Coverage Target: 90%+

### Test Categories
1. **Model Tests** - Validation, relationships, cascade delete
2. **API Tests** - CRUD, pagination, filtering, search
3. **Permission Tests** - Auth, access control, drafts
4. **Auth Tests** - Register, login, tokens, social

### Test Data
- Factory Boy for test data generation
- Separate test database

## Implementation Order

1. Core app - Custom User model
2. Taxonomy app - Categories, Tags
3. Recipe app - Recipe, Ingredient, NutritionInfo models
4. Recipe API - ViewSets, serializers, permissions
5. Interaction app - Rating, Favorite, Comment
6. Authentication - JWT + social auth
7. Image handling - Upload, resize, S3
8. Filtering & search
9. Rate limiting
10. Tests
