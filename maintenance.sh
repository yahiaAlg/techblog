#!/bin/bash

# Maintenance script for TechBlog
PROJECT_DIR="/home/yahia/techblog"
BACKUP_DIR="/home/yahia/backups/techblog"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Remove backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -exec rm {} \;

# Check and clean Docker
docker system prune -f
docker volume prune -f

# Restart services
docker-compose restart

# Check services status
docker-compose ps

# Update SSL certificates if needed
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx