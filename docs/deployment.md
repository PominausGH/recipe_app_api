# Recipe App Deployment Guide

This guide covers deploying the Recipe App API to a production VPS.

## Requirements

- Ubuntu 22.04 LTS (or similar)
- Docker 24.0+ and Docker Compose v2
- 2GB RAM minimum (4GB recommended)
- Domain name with DNS configured
- SSL certificate (Let's Encrypt)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/recipe_app_api.git
cd recipe_app_api

# 2. Create production environment file
cp .env.example .env.production
# Edit .env.production with your values

# 3. Set up SSL certificates (see SSL Setup section)

# 4. Deploy
./scripts/deploy.sh --build
```

## Environment Configuration

Copy `.env.example` to `.env.production` and configure:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=app.settings.prod
SECRET_KEY=<generate-with-python-secrets>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_HOST=db
DB_NAME=recipe_app
DB_USER=recipe_user
DB_PASS=<secure-password>

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (SendGrid example)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<your-sendgrid-api-key>
DEFAULT_FROM_EMAIL=Recipe App <noreply@yourdomain.com>

# Frontend URL for email links
FRONTEND_URL=https://yourdomain.com
```

### Generating a Secret Key

```python
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## SSL Setup with Let's Encrypt

### Initial Certificate

```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Stop any running services on port 80
sudo systemctl stop nginx  # if installed

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/

# Set permissions
sudo chown $USER:$USER ./nginx/ssl/*.pem
chmod 600 ./nginx/ssl/*.pem
```

### Auto-Renewal

Add to crontab (`sudo crontab -e`):

```bash
0 3 * * * certbot renew --quiet --post-hook "docker compose -f /path/to/recipe_app_api/docker-compose.prod.yml restart nginx"
```

## Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install docker-compose-plugin

# Verify
docker --version
docker compose version
```

## Deployment

### First Deployment

```bash
./scripts/deploy.sh --build
```

### Subsequent Deployments

```bash
./scripts/deploy.sh
```

### Manual Commands

```bash
# Build containers
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec app python manage.py migrate

# Collect static files
docker compose -f docker-compose.prod.yml exec app python manage.py collectstatic --noinput

# Create superuser
docker compose -f docker-compose.prod.yml exec app python manage.py createsuperuser

# Seed sample data
docker compose -f docker-compose.prod.yml exec app python manage.py seed_recipes

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop all services
docker compose -f docker-compose.prod.yml down
```

## Database Backup

### Manual Backup

```bash
./scripts/backup-db.sh
```

### Automated Backups

Add to crontab:

```bash
0 2 * * * /path/to/recipe_app_api/scripts/backup-db.sh
```

### Restore from Backup

```bash
# Stop the app (keep db running)
docker compose -f docker-compose.prod.yml stop app

# Restore
gunzip -c /backups/recipe_app_backup_2024-01-15_02-00-00.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME

# Start the app
docker compose -f docker-compose.prod.yml start app
```

## Health Check

The API provides a health check endpoint:

```bash
curl https://yourdomain.com/api/health/
# Returns: {"status": "healthy", "database": "connected"}
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs app

# Check if database is ready
docker compose -f docker-compose.prod.yml exec db pg_isready
```

### Database connection errors

```bash
# Verify environment variables
docker compose -f docker-compose.prod.yml exec app env | grep DB_

# Test database connection
docker compose -f docker-compose.prod.yml exec db psql -U $DB_USER -d $DB_NAME -c "SELECT 1"
```

### SSL certificate issues

```bash
# Check certificate expiry
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

### Nginx issues

```bash
# Test nginx config
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# View nginx logs
docker compose -f docker-compose.prod.yml logs nginx
```

### Static files not loading

```bash
# Re-collect static files
docker compose -f docker-compose.prod.yml exec app python manage.py collectstatic --noinput --clear

# Check nginx is serving static files
docker compose -f docker-compose.prod.yml exec nginx ls -la /app/static/
```

## Monitoring

### Check service status

```bash
docker compose -f docker-compose.prod.yml ps
```

### Resource usage

```bash
docker stats
```

### Disk usage

```bash
docker system df
```

### Clean up unused resources

```bash
docker system prune -a
```

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] Database password is secure
- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] Regular database backups scheduled
- [ ] `.env.production` is not in version control
- [ ] SSH key authentication enabled
- [ ] Fail2ban installed (optional but recommended)

## Updating the Application

```bash
cd /path/to/recipe_app_api
git pull origin main
./scripts/deploy.sh --build
```

## Rollback

If a deployment fails:

```bash
# View recent commits
git log --oneline -5

# Rollback to previous commit
git checkout <previous-commit-hash>
./scripts/deploy.sh --build
```
