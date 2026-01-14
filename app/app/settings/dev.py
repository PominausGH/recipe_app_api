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
