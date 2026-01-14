# Phase 2: Security & Configuration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add CORS support, environment-based configuration, security headers, and stricter auth rate limiting to prepare for production deployment.

**Architecture:** Split settings into base/dev/production files. CORS handled by django-cors-headers middleware. Auth throttles as custom classes applied to specific views.

**Tech Stack:** Django 3.2, django-cors-headers, djangorestframework throttling

---

## Task 1: Install and Configure CORS

**Files:**
- Modify: `requirements.txt`
- Modify: `app/app/settings/base.py:13-40` (INSTALLED_APPS and MIDDLEWARE)

**Step 1: Add django-cors-headers to requirements**

Edit `requirements.txt` to add:
```
django-cors-headers>=4.0.0,<5.0
```

**Step 2: Rebuild Docker to install dependency**

Run:
```bash
docker-compose build
```
Expected: Build completes successfully

**Step 3: Add corsheaders to INSTALLED_APPS**

In `app/app/settings/base.py`, add `"corsheaders"` to INSTALLED_APPS after the third-party apps comment:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    # Local apps
    "core",
    "taxonomy",
    "recipe",
    "interaction",
]
```

**Step 4: Add CORS middleware**

In `app/app/settings/base.py`, add CorsMiddleware at the top of MIDDLEWARE (must be before CommonMiddleware):

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

**Step 5: Add default CORS settings to base**

Add at end of `app/app/settings/base.py`:

```python
# CORS settings (override in production)
CORS_ALLOWED_ORIGINS: list[str] = []
CORS_ALLOW_CREDENTIALS = True
```

**Step 6: Add permissive CORS for dev**

Add at end of `app/app/settings/dev.py`:

```python
# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
```

**Step 7: Verify CORS works in dev**

Run:
```bash
docker-compose up -d
curl -I -X OPTIONS http://localhost:8000/api/recipes/ -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET"
```
Expected: Response includes `Access-Control-Allow-Origin: http://localhost:5173`

**Step 8: Commit**

```bash
git add requirements.txt app/app/settings/base.py app/app/settings/dev.py
git commit -m "feat: add CORS support with django-cors-headers"
```

---

## Task 2: Create Production Settings File

**Files:**
- Create: `app/app/settings/prod.py`

**Step 1: Create production settings file**

Create `app/app/settings/prod.py`:

```python
import os

from .base import *  # noqa: F401, F403

DEBUG = False

# Security: Must be set via environment
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required in production")

# Database from environment
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASS"),
    }
}

# Static and media files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"  # noqa: F405
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# CORS: Only allow specific origins in production
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOWED_ORIGINS = [o for o in CORS_ALLOWED_ORIGINS if o]  # Remove empty strings

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

**Step 2: Verify settings load without error (with mock env vars)**

Run:
```bash
docker-compose exec app python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
os.environ['ALLOWED_HOSTS'] = 'example.com'
os.environ['DB_HOST'] = 'db'
os.environ['DB_NAME'] = 'test'
os.environ['DB_USER'] = 'test'
os.environ['DB_PASS'] = 'test'
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings.prod'
from django.conf import settings
print('DEBUG:', settings.DEBUG)
print('SECURE_SSL_REDIRECT:', settings.SECURE_SSL_REDIRECT)
"
```
Expected: `DEBUG: False` and `SECURE_SSL_REDIRECT: True`

**Step 3: Commit**

```bash
git add app/app/settings/prod.py
git commit -m "feat: add production settings with security headers"
```

---

## Task 3: Create Environment Example File

**Files:**
- Create: `.env.example`

**Step 1: Create environment example file**

Create `.env.example` in project root:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=app.settings.prod
SECRET_KEY=your-secret-key-here-use-python-secrets-module-to-generate
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_HOST=db
DB_NAME=recipe_app
DB_USER=recipe_user
DB_PASS=secure-password-here

# CORS (comma-separated list of allowed origins)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (for Phase 1 - can leave empty for now)
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

**Step 2: Add .env to .gitignore if not present**

Check and add to `.gitignore`:
```bash
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore
```

**Step 3: Commit**

```bash
git add .env.example .gitignore
git commit -m "docs: add environment variables example file"
```

---

## Task 4: Add Auth Rate Limiting - Test First

**Files:**
- Modify: `app/core/throttling.py`
- Modify: `app/core/tests/test_throttling.py`

**Step 1: Write failing tests for login throttle**

Add to `app/core/tests/test_throttling.py`:

```python
from core.throttling import LoginRateThrottle, RegistrationRateThrottle


class LoginThrottleTests(TestCase):
    """Tests for login endpoint rate limiting."""

    def test_login_throttle_class_exists(self):
        """Test LoginRateThrottle class is defined."""
        self.assertTrue(hasattr(LoginRateThrottle, "rate"))

    def test_login_throttle_rate_is_strict(self):
        """Test login throttle has strict rate limit."""
        throttle = LoginRateThrottle()
        # Should be much stricter than default anon rate
        self.assertEqual(throttle.rate, "5/minute")

    def test_login_throttle_scope(self):
        """Test login throttle has correct scope."""
        throttle = LoginRateThrottle()
        self.assertEqual(throttle.scope, "login")


class RegistrationThrottleTests(TestCase):
    """Tests for registration endpoint rate limiting."""

    def test_registration_throttle_class_exists(self):
        """Test RegistrationRateThrottle class is defined."""
        self.assertTrue(hasattr(RegistrationRateThrottle, "rate"))

    def test_registration_throttle_rate(self):
        """Test registration throttle rate."""
        throttle = RegistrationRateThrottle()
        self.assertEqual(throttle.rate, "3/minute")

    def test_registration_throttle_scope(self):
        """Test registration throttle has correct scope."""
        throttle = RegistrationRateThrottle()
        self.assertEqual(throttle.scope, "registration")
```

**Step 2: Run tests to verify they fail**

Run:
```bash
docker-compose exec app pytest app/core/tests/test_throttling.py -v -k "Login or Registration"
```
Expected: FAIL with `ImportError` or `AttributeError`

**Step 3: Implement throttle classes**

Add to `app/core/throttling.py`:

```python
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RecipeCreateThrottle(UserRateThrottle):
    """
    Throttle for recipe creation.
    Limits authenticated users to 20 recipe creations per day.
    """

    scope = "recipe_create"

    def allow_request(self, request, view):
        """Only throttle POST requests (recipe creation)."""
        if request.method != "POST":
            return True
        return super().allow_request(request, view)


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst protection.
    Prevents rapid-fire requests from authenticated users.
    """

    scope = "burst"
    rate = "60/minute"


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained rate limiting.
    Standard rate limit for authenticated users.
    """

    scope = "user"


class LoginRateThrottle(AnonRateThrottle):
    """
    Strict throttle for login attempts.
    Prevents brute force password attacks.
    """

    scope = "login"
    rate = "5/minute"


class RegistrationRateThrottle(AnonRateThrottle):
    """
    Throttle for registration attempts.
    Prevents spam account creation.
    """

    scope = "registration"
    rate = "3/minute"
```

**Step 4: Run tests to verify they pass**

Run:
```bash
docker-compose exec app pytest app/core/tests/test_throttling.py -v -k "Login or Registration"
```
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add app/core/throttling.py app/core/tests/test_throttling.py
git commit -m "feat: add strict rate limiting for login and registration"
```

---

## Task 5: Apply Throttles to Auth Views

**Files:**
- Modify: `app/core/views.py`
- Modify: `app/core/urls.py`

**Step 1: Update RegisterView to use RegistrationRateThrottle**

Modify `app/core/views.py`:

```python
from core.serializers import UserProfileSerializer, UserRegistrationSerializer
from core.throttling import LoginRateThrottle, RegistrationRateThrottle
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(generics.CreateAPIView):
    """View for user registration."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]


class MeView(generics.RetrieveUpdateAPIView):
    """View for current user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user


class LogoutView(APIView):
    """View to blacklist refresh token on logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
```

**Step 2: Create custom login view with throttling**

Add to `app/core/views.py` (after LogoutView):

```python
from rest_framework_simplejwt.views import TokenObtainPairView


class ThrottledLoginView(TokenObtainPairView):
    """Login view with strict rate limiting to prevent brute force attacks."""

    throttle_classes = [LoginRateThrottle]
```

**Step 3: Update URLs to use throttled login view**

Modify `app/core/urls.py`:

```python
from core import views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "auth"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.ThrottledLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
]
```

**Step 4: Run existing auth tests to verify nothing broke**

Run:
```bash
docker-compose exec app pytest app/core/tests/test_auth_api.py -v
```
Expected: All existing tests PASS

**Step 5: Commit**

```bash
git add app/core/views.py app/core/urls.py
git commit -m "feat: apply strict throttling to login and registration endpoints"
```

---

## Task 6: Add Throttle Rates to Settings

**Files:**
- Modify: `app/app/settings/base.py`

**Step 1: Add new throttle scopes to settings**

In `app/app/settings/base.py`, update DEFAULT_THROTTLE_RATES:

```python
"DEFAULT_THROTTLE_RATES": {
    "anon": "100/hour",
    "user": "1000/hour",
    "recipe_create": "20/day",
    "login": "5/minute",
    "registration": "3/minute",
},
```

**Step 2: Update throttle settings test**

Add to `app/core/tests/test_throttling.py` in `ThrottlingConfigTests`:

```python
def test_auth_throttle_rates_configured(self):
    """Test auth-specific throttle rates are configured."""
    rates = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]

    self.assertIn("login", rates)
    self.assertIn("registration", rates)
    self.assertEqual(rates["login"], "5/minute")
    self.assertEqual(rates["registration"], "3/minute")
```

**Step 3: Run all throttle tests**

Run:
```bash
docker-compose exec app pytest app/core/tests/test_throttling.py -v
```
Expected: All tests PASS

**Step 4: Commit**

```bash
git add app/app/settings/base.py app/core/tests/test_throttling.py
git commit -m "feat: add login and registration throttle rates to settings"
```

---

## Task 7: Add Health Check Endpoint

**Files:**
- Modify: `app/core/views.py`
- Modify: `app/core/urls.py`
- Modify: `app/core/tests/test_auth_api.py`

**Step 1: Write failing test for health check**

Add to `app/core/tests/test_auth_api.py`:

```python
HEALTH_URL = reverse("auth:health")


class HealthCheckTests(TestCase):
    """Tests for health check endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        """Test health check endpoint returns 200 when healthy."""
        res = self.client.get(HEALTH_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "healthy")

    def test_health_check_includes_database_status(self):
        """Test health check reports database connection status."""
        res = self.client.get(HEALTH_URL)

        self.assertIn("database", res.data)
```

**Step 2: Run test to verify it fails**

Run:
```bash
docker-compose exec app pytest app/core/tests/test_auth_api.py::HealthCheckTests -v
```
Expected: FAIL with `NoReverseMatch`

**Step 3: Implement health check view**

Add to `app/core/views.py`:

```python
from django.db import connection
from rest_framework.decorators import api_view, permission_classes, throttle_classes


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])  # No throttling on health checks
def health_check(request):
    """Health check endpoint for monitoring and container orchestration."""
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception as e:
        return Response(
            {"status": "unhealthy", "database": "disconnected", "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({"status": "healthy", "database": db_status})
```

**Step 4: Add URL for health check**

Update `app/core/urls.py`:

```python
from core import views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "auth"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.ThrottledLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path("health/", views.health_check, name="health"),
]
```

**Step 5: Run tests to verify they pass**

Run:
```bash
docker-compose exec app pytest app/core/tests/test_auth_api.py::HealthCheckTests -v
```
Expected: Both tests PASS

**Step 6: Commit**

```bash
git add app/core/views.py app/core/urls.py app/core/tests/test_auth_api.py
git commit -m "feat: add health check endpoint for monitoring"
```

---

## Task 8: Final Verification

**Step 1: Run full test suite**

Run:
```bash
docker-compose exec app pytest -v
```
Expected: All tests PASS

**Step 2: Verify CORS headers work**

Run:
```bash
docker-compose up -d
curl -I -X OPTIONS http://localhost:8000/api/auth/login/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST"
```
Expected: Response includes `Access-Control-Allow-Origin`

**Step 3: Verify health check works**

Run:
```bash
curl http://localhost:8000/api/auth/health/
```
Expected: `{"status":"healthy","database":"connected"}`

**Step 4: Run linting**

Run:
```bash
docker-compose exec app flake8 app/
```
Expected: No errors

**Step 5: Final commit for any cleanup**

If any cleanup needed:
```bash
git add -A
git commit -m "chore: phase 2 cleanup and verification"
```

---

## Summary

After completing all tasks, you will have:

1. **CORS support** - Frontend can call backend across origins
2. **Production settings** - Separate config with security headers
3. **Environment variables** - All secrets from environment
4. **Auth rate limiting** - 5 login attempts/min, 3 registrations/min
5. **Health check** - `/api/auth/health/` for monitoring

**Files modified:**
- `requirements.txt` - Added django-cors-headers
- `app/app/settings/base.py` - CORS middleware, throttle rates
- `app/app/settings/dev.py` - Permissive CORS for development
- `app/app/settings/prod.py` - New file with security headers
- `app/core/throttling.py` - LoginRateThrottle, RegistrationRateThrottle
- `app/core/views.py` - ThrottledLoginView, health_check
- `app/core/urls.py` - Updated login URL, added health URL
- `app/core/tests/test_throttling.py` - New throttle tests
- `app/core/tests/test_auth_api.py` - Health check tests
- `.env.example` - New file documenting env vars
- `.gitignore` - Ensure .env is ignored
