import os  # noqa: E402

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST", "db"),
        "NAME": os.environ.get("DB_NAME", "devdb"),
        "USER": os.environ.get("DB_USER", "devuser"),
        "PASSWORD": os.environ.get("DB_PASS", "password"),
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Higher throttle rates for development/testing
REST_FRAMEWORK.update(  # noqa: F405
    {
        "DEFAULT_THROTTLE_RATES": {
            "anon": "100/hour",
            "user": "1000/hour",
            "recipe_create": "20/day",
            "auth": "1000/minute",
        },
    }
)

# Use local memory cache for dev/testing (isolated per process)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email backend for development - prints to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Recipe App <noreply@recipeapp.local>"
