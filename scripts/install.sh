#!/bin/bash
# Router Supervisor Installation Script
# This script sets up the complete environment inside the Docker container

set -e  # Exit on any error

echo "🚀 Starting Router Supervisor Installation..."
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the Docker container
if [ ! -f /.dockerenv ]; then
    print_warning "This script is designed to run inside a Docker container"
fi

# Set working directory
cd /code

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
python3 -c "
import time
import psycopg2
import os

max_retries = 60
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=os.environ.get('SQL_HOST', 'db'),
            database=os.environ.get('SQL_DATABASE', 'routerdb'),
            user=os.environ.get('SQL_USER', 'user'),
            password=os.environ.get('SQL_PASSWORD', 'password'),
            port=os.environ.get('SQL_PORT', '5432')
        )
        conn.close()
        print('PostgreSQL is ready!')
        break
    except psycopg2.OperationalError:
        retry_count += 1
        print(f'Waiting for PostgreSQL... ({retry_count}/{max_retries})')
        time.sleep(1)
else:
    print('Failed to connect to PostgreSQL after maximum retries')
    exit(1)
"

print_success "PostgreSQL is ready!"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p /code/static /code/media /tmp/metrics /code/logs
chmod -R 755 /code/static /code/media /tmp/metrics /code/logs

# Set up Python path
export PYTHONPATH="/code:$PYTHONPATH"

# Check Django configuration
print_status "Checking Django configuration..."
cd /code && python3 router_supervisor/manage.py check --deploy || {
    print_warning "Django system check found issues, but continuing..."
}

# Run our custom database installation script
print_status "Running database installation script..."
cd /code && python3 scripts/install_db.py

# Create a health check endpoint test
print_status "Testing application health..."
cd /code && python3 -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'router_supervisor.prod_settings')
django.setup()

from django.test.utils import get_runner
from django.core import management

# Run a simple check
try:
    management.call_command('check', verbosity=0)
    print('✅ Django application check passed!')
except Exception as e:
    print(f'❌ Django application check failed: {e}')
    exit(1)
"

# Set up log rotation (optional)
print_status "Setting up logging..."
cat > /etc/logrotate.d/router-supervisor << 'EOF'
/code/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

# Create a startup summary
print_status "Creating startup summary..."
cat > /code/startup_info.txt << EOF
Router Supervisor Installation Summary
=====================================
Installation Date: $(date)
Docker Container: $(hostname)
Python Version: $(python3 --version)
Django Version: $(cd /code && python3 -c "import django; print(django.get_version())")

Database Configuration:
- Host: ${SQL_HOST:-db}
- Database: ${SQL_DATABASE:-routerdb}
- User: ${SQL_USER:-user}
- Port: ${SQL_PORT:-5432}

Application URLs:
- Main Dashboard: http://localhost/
- Admin Panel: http://localhost/admin/
- API Endpoint: http://localhost/api/
- Health Check: http://localhost/health/

Default Admin Credentials:
- Username: ${ADMIN_USER:-admin}
- Email: ${ADMIN_EMAIL:-admin@telecom-sudparis.eu}
- Password: ${ADMIN_PASSWORD:-admin123}

Static Files: /code/static/
Media Files: /code/media/
Logs: /code/logs/

Installation completed successfully!
EOF

print_success "Installation completed successfully!"
echo "================================================"
echo "📋 Summary:"
echo "   ✅ Database setup completed"
echo "   ✅ Migrations applied"
echo "   ✅ Static files collected"
echo "   ✅ Admin user created"
echo "   ✅ Initial data loaded"
echo ""
echo "🌐 Access your application at:"
echo "   - Main Dashboard: http://localhost/"
echo "   - Admin Panel: http://localhost/admin/"
echo "   - PgAdmin: http://localhost:5050/"
echo ""
echo "📁 Installation details saved to: /code/startup_info.txt"
echo "================================================"
