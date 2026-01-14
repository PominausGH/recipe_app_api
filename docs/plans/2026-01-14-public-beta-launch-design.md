# Public Beta Launch Plan

## Overview

This document outlines the work required to launch the Recipe App as a public beta. The app has solid core functionality (95% API complete, 90% frontend complete) but needs authentication improvements, security hardening, and production deployment configuration.

**Target:** Public beta launch on Hostinger VPS

**Current State:**
- Core API: 95% ready
- Frontend: 90% ready
- Code Quality: 90% (pre-commit hooks, linting, types)
- Security: 65% (needs CORS, HTTPS, auth rate limiting)
- Auth: 60% (needs email verification, password reset)
- Deployment: 30% (needs production config)

---

## Phase 1: Authentication Completeness

**Priority:** High - Users cannot trust the app without account recovery

### 1.1 Email Verification Flow

**Backend:**
- Add `is_email_verified` field to User model (default False)
- Add `EmailVerificationToken` model (token, user, created_at, expires_at)
- `POST /api/auth/register/` - Generate token, send verification email, return success
- `POST /api/auth/verify-email/` - Accept token, activate account
- `POST /api/auth/resend-verification/` - Resend verification email (rate limited)

**Frontend:**
- Registration success page: "Check your email to verify your account"
- Email verification page: Accepts token from URL, calls verify endpoint
- Login page: Show message if account not verified

**Email template:**
- Subject: "Verify your Recipe App account"
- Body: Welcome message + verification link + expiry notice (24 hours)

### 1.2 Password Reset Flow

**Backend:**
- Add `PasswordResetToken` model (token, user, created_at, expires_at)
- `POST /api/auth/forgot-password/` - Accept email, send reset link (always return success)
- `POST /api/auth/reset-password/` - Accept token + new password, update user

**Frontend:**
- Forgot password page: Email input form
- Reset password page: New password form (accessed via email link)
- Success confirmation page

**Email template:**
- Subject: "Reset your Recipe App password"
- Body: Reset link + expiry notice (1 hour) + "ignore if not requested"

### 1.3 Email Infrastructure

**Service:** SendGrid, Mailgun, or AWS SES (all have free tiers)

**Configuration:**
```python
# settings/production.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Recipe App <noreply@yourdomain.com>'
```

**Dev environment:** Use console backend for testing
```python
# settings/dev.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## Phase 2: Security & Configuration

**Priority:** High - Blockers that prevent the app from functioning

### 2.1 CORS Configuration

**Install:**
```bash
pip install django-cors-headers
```

**Configure:**
```python
# settings/base.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    ...
]

# settings/production.py
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
CORS_ALLOW_CREDENTIALS = True
```

### 2.2 Environment-Based Settings

**Required environment variables:**
```bash
# Django
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_HOST=db
DB_NAME=recipe_app
DB_USER=recipe_user
DB_PASS=<secure-password>

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
```

**Settings updates:**
```python
# settings/base.py
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

### 2.3 Security Headers

```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### 2.4 Auth Endpoint Rate Limiting

```python
# core/throttling.py
class LoginRateThrottle(AnonRateThrottle):
    rate = '5/min'

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '3/min'

class PasswordResetRateThrottle(AnonRateThrottle):
    rate = '3/min'
```

**Apply to views:**
```python
class LoginView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]

class RegisterView(CreateAPIView):
    throttle_classes = [RegistrationRateThrottle]

class ForgotPasswordView(APIView):
    throttle_classes = [PasswordResetRateThrottle]
```

---

## Phase 3: Production Deployment

**Priority:** High - Required to launch

### 3.1 Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env.production
    volumes:
      - static_data:/app/static
      - media_data:/app/media
    depends_on:
      - db
    command: gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 3

  db:
    image: postgres:13-alpine
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_data:/app/static:ro
      - media_data:/app/media:ro
    depends_on:
      - app

volumes:
  postgres_data:
  static_data:
  media_data:
```

### 3.2 Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;

    upstream django {
        server app:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        client_max_body_size 10M;

        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 7d;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 3.3 SSL with Let's Encrypt

**Initial setup on VPS:**
```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Get certificate (stop nginx first)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certs to nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/
```

**Auto-renewal cron:**
```bash
# /etc/cron.d/certbot-renew
0 3 * * * root certbot renew --quiet --post-hook "docker-compose -f /path/to/docker-compose.prod.yml restart nginx"
```

### 3.4 Health Check Endpoint

```python
# core/views.py
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    try:
        connection.ensure_connection()
        return Response({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return Response({'status': 'unhealthy', 'error': str(e)}, status=503)
```

```python
# core/urls.py
urlpatterns = [
    ...
    path('health/', health_check, name='health-check'),
]
```

### 3.5 Database Backup

```bash
# scripts/backup-db.sh
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y-%m-%d_%H-%M-%S)
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete  # Keep 7 days
```

**Cron job:**
```bash
0 2 * * * /path/to/scripts/backup-db.sh
```

### 3.6 Deployment Script

```bash
# scripts/deploy.sh
#!/bin/bash
set -e

cd /path/to/recipe_app_api

# Pull latest code
git pull origin main

# Build and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec app python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec app python manage.py collectstatic --noinput

echo "Deployment complete!"
```

---

## Phase 4: Pre-Launch Polish

**Priority:** Medium - Improves beta experience

### 4.1 Error Pages

**Create templates:**
- `templates/404.html` - Friendly "page not found" with link to home
- `templates/500.html` - "Something went wrong" with contact info

**Configure:**
```python
# settings/base.py
TEMPLATES = [
    {
        ...
        'DIRS': [BASE_DIR / 'templates'],
    },
]
```

### 4.2 Frontend Checklist

- [ ] All API calls show loading spinners
- [ ] Form validation errors display clearly
- [ ] Network error states handled gracefully
- [ ] Mobile responsive (test 375px, 768px, 1024px widths)
- [ ] Empty states for lists (no recipes, no followers, etc.)

### 4.3 Seed Data

Enhance existing `seed_recipes` command or create sample data:
- 5-10 sample recipes across different categories
- 2-3 demo user accounts
- Sample comments and ratings

### 4.4 Documentation

**Create `.env.example`:**
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DB_HOST=db
DB_NAME=recipe_app
DB_USER=recipe_user
DB_PASS=secure-password

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-key
```

**Create `docs/deployment.md`:**
- VPS requirements (Ubuntu 22.04, 2GB RAM minimum)
- Docker/Docker Compose installation
- SSL certificate setup
- Environment configuration
- Deployment commands
- Backup/restore procedures
- Troubleshooting common issues

### 4.5 Beta Feedback Mechanism

Options:
1. GitHub Issues (if repo is public)
2. Simple feedback form in footer → sends email
3. External service (Canny, UserVoice free tier)

Recommendation: Start with a mailto link or simple form, upgrade later.

---

## Implementation Order

```
Week 1:
├── Phase 2: Security & Config (1-2 days)
│   ├── CORS setup
│   ├── Environment variables
│   ├── Security headers
│   └── Auth rate limiting
│
└── Phase 1: Start Authentication (3-4 days)
    ├── Email infrastructure setup
    ├── Email verification backend
    └── Email verification frontend

Week 2:
├── Phase 1: Complete Authentication
│   ├── Password reset backend
│   └── Password reset frontend
│
└── Phase 3: Start Deployment
    ├── Production docker-compose
    └── Nginx configuration

Week 3:
├── Phase 3: Complete Deployment
│   ├── SSL setup on VPS
│   ├── Health check endpoint
│   ├── Backup scripts
│   └── Deploy script
│
└── Phase 4: Polish
    ├── Error pages
    ├── Frontend review
    ├── Seed data
    └── Documentation

Launch: End of Week 3
```

---

## Post-Beta Roadmap

Features to consider after successful beta launch:

1. **Two-factor authentication** - Enhanced security
2. **S3 for media storage** - Scalability
3. **Redis caching** - Performance for feed
4. **Full-text search** - Elasticsearch integration
5. **Real-time notifications** - WebSocket support
6. **Mobile app** - React Native or Flutter
7. **Social sharing** - Open Graph tags, share buttons
8. **Moderation tools** - User reports, admin dashboard

---

## Success Criteria

Beta is ready to launch when:

- [ ] Users can register with email verification
- [ ] Users can reset forgotten passwords
- [ ] App runs on Hostinger VPS with HTTPS
- [ ] Core flows work on mobile browsers
- [ ] Health check endpoint returns healthy
- [ ] Database backups are automated
- [ ] At least 5 sample recipes exist
- [ ] Feedback mechanism is in place
