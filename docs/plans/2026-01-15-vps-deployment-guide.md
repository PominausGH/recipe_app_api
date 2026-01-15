# VPS Deployment Guide

Guide for deploying the Recipe App API to a VPS with Docker already installed.

## Prerequisites

- VPS with Docker and Docker Compose installed
- Domain pointed to VPS IP address
- SSL certificates (fullchain.pem and privkey.pem)
- Private GitHub repo access

## 1. Set Up GitHub Access

Generate a deploy key on your VPS:

```bash
ssh-keygen -t ed25519 -C "recipe-app-deploy" -f ~/.ssh/recipe_deploy_key

# Show the public key - add this to GitHub repo Settings > Deploy Keys
cat ~/.ssh/recipe_deploy_key.pub

# Configure SSH to use this key for GitHub
echo "Host github.com
  IdentityFile ~/.ssh/recipe_deploy_key" >> ~/.ssh/config
```

Clone the repository:

```bash
git clone git@github.com:PominausGH/recipe_app_api.git
cd recipe_app_api
```

## 2. Environment Configuration

Create your production environment file:

```bash
cp .env.example .env.production
nano .env.production
```

Required values:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ALLOWED_HOSTS` | Your domain (e.g., `recipes.yourdomain.com`) |
| `DB_PASS` | Strong password for PostgreSQL |
| `CORS_ALLOWED_ORIGINS` | Your frontend URL(s) |
| Email settings | Configure if using email features |

## 3. SSL Certificates

Copy your SSL certificates to the nginx folder:

```bash
cp /path/to/your/fullchain.pem nginx/ssl/fullchain.pem
cp /path/to/your/privkey.pem nginx/ssl/privkey.pem
chmod 600 nginx/ssl/*.pem
```

## 4. Deploy

Run the deployment script:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh --build
```

This will:
- Build the Docker containers
- Start PostgreSQL, Django app, and nginx
- Run database migrations
- Collect static files
- Run health check at `/api/health/`

Verify deployment:

```bash
# Check containers are running
docker ps

# Check logs if needed
docker-compose -f docker-compose.prod.yml logs -f

# Test from your machine
curl https://yourdomain.com/api/health/
```

## Ongoing Maintenance

### View Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f app
```

### Backup Database

```bash
./scripts/backup-db.sh
```

### Redeploy After Code Changes

SSH into your VPS and run:

```bash
cd recipe_app_api
./scripts/deploy.sh
```

Use `--build` flag if dependencies changed:

```bash
./scripts/deploy.sh --build
```

### Stop Services

```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Services

```bash
docker-compose -f docker-compose.prod.yml restart
```
