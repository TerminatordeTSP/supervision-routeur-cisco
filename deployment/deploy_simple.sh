#!/bin/bash

# THE ONLY deployment script you need - simple and effective
# Deploys Django app with Gunicorn (NOT runserver) to server

set -e

# Variables de configuration
SERVER_HOST="supervision-server"  # Uses SSH config with deploy key
REMOTE_PATH="supervision-routeur-cisco"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🚀 Django Deployment (with Gunicorn, NOT runserver)"
echo "===================================================="

# Test SSH connection
echo -e "${BLUE}Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=5 "$SERVER_HOST" "echo 'SSH OK'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to $SERVER_HOST${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection OK${NC}"

# Deploy
echo -e "${BLUE}Syncing files to server...${NC}"
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.vscode' \
    --exclude='*.log' \
    ./ "$SERVER_HOST:$REMOTE_PATH/"

echo -e "${BLUE}Deploying application...${NC}"
ssh "$SERVER_HOST" "
    # Go to project directory
    cd $REMOTE_PATH || { echo 'Project directory not found'; exit 1; }
    
    # Stop containers (Docker Compose V2 syntax)
    echo 'Stopping containers...'
    docker compose down 2>/dev/null || true
    docker compose -f deployment/docker-compose.prod.yml down 2>/dev/null || true
    
    # Clean up
    echo 'Cleaning up...'
    docker system prune -f
    
    # Start with production config (uses Gunicorn)
    echo 'Starting containers with Gunicorn...'
    docker compose -f deployment/docker-compose.prod.yml up -d --build
    
    # Wait for startup
    echo 'Waiting for Django to start...'
    sleep 30
    
    # Check status
    echo 'Container status:'
    docker compose -f deployment/docker-compose.prod.yml ps
    
    # Test Django
    echo 'Testing Django...'
    if curl -f http://localhost:8080/health/ >/dev/null 2>&1; then
        echo '✅ Django is responding with Gunicorn'
    else
        echo '❌ Django is not responding'
        echo 'Django logs:'
        docker logs router_django_prod 2>/dev/null | tail -10 || echo 'No logs available'
    fi
    
    # Show external IP
    SERVER_IP=\$(hostname -I | awk '{print \$1}' 2>/dev/null || echo '172.16.10.40')
    echo \"\"
    echo \"🌐 Application should be accessible at:\"
    echo \"   http://\$SERVER_IP:8080/\"
    echo \"   (Django with Gunicorn, port 8080)\"
"

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo "Django is running with Gunicorn (NOT python manage.py runserver)"
