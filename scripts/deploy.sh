#!/bin/bash
# Deployment script for Recipe App
# Usage: ./scripts/deploy.sh [--build]

set -e

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$APP_DIR"

echo "=== Recipe App Deployment ==="
echo "Directory: $APP_DIR"
echo "Started at: $(date)"
echo ""

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "ERROR: .env.production file not found!"
    echo "Please copy .env.example to .env.production and configure it."
    exit 1
fi

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build if requested or if first deploy
if [ "$1" == "--build" ] || [ ! "$(docker images -q recipe_app_api-app 2>/dev/null)" ]; then
    echo "Building containers..."
    docker-compose -f "$COMPOSE_FILE" build
fi

# Start/restart services
echo "Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Run migrations
echo "Running migrations..."
docker-compose -f "$COMPOSE_FILE" exec -T app python manage.py migrate

# Collect static files
echo "Collecting static files..."
docker-compose -f "$COMPOSE_FILE" exec -T app python manage.py collectstatic --noinput

# Health check
echo "Running health check..."
sleep 3
HEALTH_RESPONSE=$(curl -s http://localhost/api/health/ || echo '{"status":"error"}')
echo "Health check response: $HEALTH_RESPONSE"

echo ""
echo "=== Deployment Complete ==="
echo "Finished at: $(date)"
echo ""
echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "To stop: docker-compose -f $COMPOSE_FILE down"
