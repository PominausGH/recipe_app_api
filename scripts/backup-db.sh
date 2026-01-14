#!/bin/bash
# Database backup script for Recipe App
# Run this with cron: 0 2 * * * /path/to/scripts/backup-db.sh

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
KEEP_DAYS="${KEEP_DAYS:-7}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/recipe_app_backup_$DATE.sql"

echo "Starting database backup at $(date)"

# Perform backup
docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --clean \
    --if-exists \
    > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
echo "Backup created: ${BACKUP_FILE}.gz"

# Remove old backups
find "$BACKUP_DIR" -name "recipe_app_backup_*.sql.gz" -mtime +$KEEP_DAYS -delete
echo "Removed backups older than $KEEP_DAYS days"

echo "Backup completed at $(date)"
