"""
Download food images for all recipes using free APIs.
Tier 1: TheMealDB (recipe-specific, high quality)
Tier 2: Wikimedia Commons (search-based)
Tier 3: Generic cuisine images
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# SSL context for downloads
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

MEDIA_DIR = "/opt/docker/recipe_app_api/app/media/recipes"
os.makedirs(MEDIA_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; RecipeApp/1.0)"}


def safe_filename(title, recipe_id):
    """Generate a safe filename from recipe title."""
    slug = title.lower().replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return f"{recipe_id}-{slug[:50]}.jpg"


def download_image(url, filepath):
    """Download an image from a URL to a filepath."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            data = response.read()
            if len(data) < 1000:  # Too small, probably an error
                return False
            with open(filepath, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        return False


def search_themealdb(title):
    """Search TheMealDB for a recipe image."""
    try:
        # Try exact search
        query = urllib.parse.quote(title)
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read())
            if data.get("meals"):
                return data["meals"][0].get("strMealThumb")
    except Exception:
        pass
    return None


def search_wikimedia(title):
    """Search Wikimedia Commons for a food image."""
    try:
        query = urllib.parse.quote(f"{title} food dish")
        url = (
            f"https://commons.wikimedia.org/w/api.php?"
            f"action=query&generator=search&gsrsearch={query}"
            f"&gsrnamespace=6&gsrlimit=3&prop=imageinfo"
            f"&iiprop=url&iiurlwidth=800&format=json"
        )
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                imageinfo = page.get("imageinfo", [])
                if imageinfo:
                    thumb = imageinfo[0].get("thumburl")
                    if thumb:
                        return thumb
    except Exception:
        pass
    return None


# Generic cuisine search terms for fallback
CUISINE_SEARCH_TERMS = {
    "indian": "Indian curry spices",
    "italian": "Italian pasta dish",
    "mexican": "Mexican tacos salsa",
    "middle-eastern": "Middle Eastern hummus falafel",
    "asian": "Asian stir fry noodles",
    "african": "African stew rice",
}


def process_recipe(recipe_id, title, cuisine):
    """Download an image for a single recipe."""
    filename = safe_filename(title, recipe_id)
    filepath = os.path.join(MEDIA_DIR, filename)

    # Skip if already downloaded
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        return recipe_id, filename, "exists"

    # Tier 1: TheMealDB
    img_url = search_themealdb(title)
    if img_url:
        # TheMealDB returns URLs like .../xxx.jpg, add /preview for smaller size
        if download_image(img_url + "/preview", filepath):
            return recipe_id, filename, "themealdb"
        if download_image(img_url, filepath):
            return recipe_id, filename, "themealdb"

    # Tier 2: Wikimedia Commons
    img_url = search_wikimedia(title)
    if img_url and download_image(img_url, filepath):
        return recipe_id, filename, "wikimedia"

    # Tier 3: Try simpler search terms
    simple_terms = title.split("(")[0].strip()  # Remove parenthetical
    if simple_terms != title:
        img_url = search_wikimedia(simple_terms)
        if img_url and download_image(img_url, filepath):
            return recipe_id, filename, "wikimedia-simple"

    # Tier 4: Search by cuisine + main ingredient
    words = title.split()[:2]
    search = " ".join(words) + " food"
    img_url = search_wikimedia(search)
    if img_url and download_image(img_url, filepath):
        return recipe_id, filename, "wikimedia-partial"

    return recipe_id, None, "failed"


def get_recipes():
    """Get all recipes from Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    sys.path.insert(0, "/app")
    import django
    django.setup()
    from recipe.models import Recipe

    recipes = Recipe.objects.select_related("category").all()
    result = []
    for r in recipes:
        cuisine = r.category.slug if r.category else "other"
        result.append((r.id, r.title, cuisine))
    return result


def update_database(results):
    """Update recipe image fields in Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    sys.path.insert(0, "/app")
    import django
    django.setup()
    from recipe.models import Recipe

    updated = 0
    for recipe_id, filename, source in results:
        if filename:
            try:
                recipe = Recipe.objects.get(id=recipe_id)
                recipe.image = f"recipes/{filename}"
                recipe.save(update_fields=["image"])
                updated += 1
            except Exception as e:
                print(f"  Error updating {recipe_id}: {e}")
    return updated


def main():
    print("=" * 60)
    print("Recipe Image Downloader")
    print("=" * 60)

    # When run on the host, we need to get recipe list from container
    # So we read from a pre-generated list file
    recipe_list_file = "/tmp/recipe_list.json"

    if os.path.exists(recipe_list_file):
        with open(recipe_list_file) as f:
            recipes = json.load(f)
        print(f"Loaded {len(recipes)} recipes from list file")
    else:
        print("ERROR: No recipe list file found at /tmp/recipe_list.json")
        print("Generate it first with: docker exec ... python -c '...'")
        sys.exit(1)

    print(f"\nDownloading images for {len(recipes)} recipes...")
    print(f"Saving to: {MEDIA_DIR}")

    results = []
    stats = {"themealdb": 0, "wikimedia": 0, "wikimedia-simple": 0,
             "wikimedia-partial": 0, "exists": 0, "failed": 0}

    # Use thread pool for concurrent downloads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for recipe_id, title, cuisine in recipes:
            future = executor.submit(process_recipe, recipe_id, title, cuisine)
            futures[future] = (recipe_id, title)

        done = 0
        for future in as_completed(futures):
            recipe_id, title = futures[future]
            try:
                rid, filename, source = future.result()
                results.append((rid, filename, source))
                stats[source] = stats.get(source, 0) + 1
                done += 1
                if done % 20 == 0:
                    print(f"  Progress: {done}/{len(recipes)} "
                          f"(mealdb:{stats['themealdb']}, "
                          f"wiki:{stats['wikimedia'] + stats['wikimedia-simple'] + stats['wikimedia-partial']}, "
                          f"failed:{stats['failed']})")
            except Exception as e:
                results.append((recipe_id, None, "failed"))
                stats["failed"] += 1
                done += 1

    print(f"\n--- Results ---")
    for source, count in sorted(stats.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {source}: {count}")

    # Save results for DB update
    with open("/tmp/image_results.json", "w") as f:
        json.dump(results, f)

    print(f"\nTotal images downloaded: {sum(1 for _, fn, _ in results if fn)}")
    print(f"Failed: {stats['failed']}")
    print(f"\nResults saved to /tmp/image_results.json")


if __name__ == "__main__":
    main()
