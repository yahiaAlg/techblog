#!/bin/bash

# Deployment script for TechBlog
PROJECT_NAME="techblog"
DOMAIN="techblog.example.com"
USER="yahia"
SERVER="135.125.106.2"  # Replace with actual IP address
DEPLOY_PATH="/home/$USER/pyapps/$PROJECT_NAME"


echo "Deploying $PROJECT_NAME to $SERVER..."

# Build and push Docker images
docker-compose build
docker-compose push

# Connect to server and deploy
ssh $USER@$SERVER << EOF
    # Navigate to project directory
    cd $DEPLOY_PATH

    # Pull latest code
    git pull origin main

    # Pull latest Docker images
    docker-compose pull

    # Stop running containers
    docker-compose down

    # Start containers with new images
    docker-compose up -d

    # Run migrations
    docker-compose exec web python manage.py migrate

    # Collect static files
    docker-compose exec web python manage.py collectstatic --no-input

    # Restart Nginx
    sudo systemctl restart nginx
EOF

echo "Deployment completed!"