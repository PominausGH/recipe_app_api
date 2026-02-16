"""
Import 300 budget-friendly, no-sugar international recipes into the Django database.
Run inside the container: docker exec recipe_app_api-app-1 python /app/import_recipes.py
"""
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from recipe.models import Recipe, Ingredient
from taxonomy.models import Category, Tag

User = get_user_model()


def get_or_create_admin():
    """Get the admin user to assign as recipe author."""
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("ERROR: No superuser found. Create one first.")
        sys.exit(1)
    print(f"Using author: {admin.email}")
    return admin


def create_categories():
    """Create cuisine categories."""
    categories = {
        "indian": "Indian",
        "italian": "Italian",
        "mexican": "Mexican",
        "middle-eastern": "Middle Eastern",
        "asian": "Asian",
        "african": "African",
    }
    created = {}
    for slug, name in categories.items():
        cat, was_created = Category.objects.get_or_create(
            slug=slug, defaults={"name": name}
        )
        created[slug] = cat
        status = "created" if was_created else "exists"
        print(f"  Category: {name} ({status})")
    return created


def create_tags():
    """Create recipe tags."""
    tag_names = [
        "vegetarian", "vegan", "gluten-free", "quick", "one-pot",
        "high-protein", "budget", "spicy", "soup", "stew", "stir-fry",
        "pasta", "curry", "salad", "breakfast", "comfort-food",
        "meal-prep", "no-sugar", "healthy", "low-carb",
    ]
    created = {}
    for name in tag_names:
        slug = slugify(name)
        tag, was_created = Tag.objects.get_or_create(
            slug=slug, defaults={"name": name.replace("-", " ").title()}
        )
        created[name] = tag
    print(f"  Tags: {len(created)} ready")
    return created


def import_recipes(recipe_list, cuisine_slug, author, categories, tags):
    """Import a list of recipes for a given cuisine."""
    category = categories.get(cuisine_slug)
    imported = 0
    skipped = 0

    for r in recipe_list:
        title = r["title"]

        # Skip if already exists
        if Recipe.objects.filter(title=title, author=author).exists():
            skipped += 1
            continue

        recipe = Recipe.objects.create(
            author=author,
            title=title,
            description=r.get("description", ""),
            instructions=r.get("instructions", ""),
            prep_time=r.get("prep_time"),
            cook_time=r.get("cook_time"),
            servings=r.get("servings", 4),
            difficulty=r.get("difficulty", "medium"),
            category=category,
            is_published=True,
        )

        # Add tags
        recipe_tags = r.get("tags", [])
        recipe_tags.append("budget")
        recipe_tags.append("no-sugar")
        for tag_name in set(recipe_tags):
            tag_slug = slugify(tag_name)
            tag_obj = tags.get(tag_name)
            if not tag_obj:
                tag_obj, _ = Tag.objects.get_or_create(
                    slug=tag_slug,
                    defaults={"name": tag_name.replace("-", " ").title()}
                )
                tags[tag_name] = tag_obj
            recipe.tags.add(tag_obj)

        # Add ingredients
        for order, ing_data in enumerate(r.get("ingredients", [])):
            name, quantity, unit = ing_data
            # Ensure quantity is valid
            qty = Decimal(str(quantity))
            if qty <= 0:
                qty = Decimal("1")
            Ingredient.objects.create(
                recipe=recipe,
                name=name,
                quantity=qty,
                unit=unit,
                order=order,
            )

        imported += 1

    return imported, skipped


def main():
    print("=" * 60)
    print("Recipe Import Script")
    print("Budget-friendly, no-sugar international recipes")
    print("=" * 60)

    print("\n1. Setting up admin user...")
    admin = get_or_create_admin()

    print("\n2. Creating categories...")
    categories = create_categories()

    print("\n3. Creating tags...")
    tags = create_tags()

    print("\n4. Importing recipes...")

    # Import each cuisine
    cuisine_modules = [
        ("indian", "recipes_indian", "INDIAN_RECIPES"),
        ("italian", "recipes_italian", "ITALIAN_RECIPES"),
        ("mexican", "recipes_mexican", "MEXICAN_RECIPES"),
        ("middle-eastern", "recipes_middle_eastern", "MIDDLE_EASTERN_RECIPES"),
        ("asian", "recipes_asian", "ASIAN_RECIPES"),
        ("african", "recipes_african", "AFRICAN_RECIPES"),
    ]

    total_imported = 0
    total_skipped = 0

    for cuisine_slug, module_name, var_name in cuisine_modules:
        print(f"\n  --- {cuisine_slug.upper()} ---")
        try:
            # Dynamic import of recipe data module
            mod = __import__(module_name)
            recipe_list = getattr(mod, var_name)
            imported, skipped = import_recipes(
                recipe_list, cuisine_slug, admin, categories, tags
            )
            total_imported += imported
            total_skipped += skipped
            print(f"  Imported: {imported}, Skipped: {skipped}")
        except ImportError as e:
            print(f"  ERROR: Could not import {module_name}: {e}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"DONE! Imported {total_imported} recipes, skipped {total_skipped}")
    print(f"Total recipes in DB: {Recipe.objects.count()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
