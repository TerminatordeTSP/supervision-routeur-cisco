#!/bin/bash

# Fixed database initialization script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database initialization...${NC}"

# Change to the router_supervisor directory
cd /code/router_supervisor

# Function to run Django management commands with proper error handling
run_django_command() {
    local command="$1"
    local description="$2"
    
    echo -e "${YELLOW}$description${NC}"
    
    if python3 manage.py $command; then
        echo -e "${GREEN}✓ $description completed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ $description failed${NC}"
        return 1
    fi
}

# Function to check if database tables exist
check_database_tables() {
    echo -e "${YELLOW}Checking if database tables exist...${NC}"
    
    # Use inspect_db instead of dbhealth if available
    if python3 manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations';\" if 'sqlite' in connection.settings_dict['ENGINE'] else \"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name='django_migrations';\" if 'postgresql' in connection.settings_dict['ENGINE'] else \"SHOW TABLES LIKE 'django_migrations';\")
result = cursor.fetchone()
print('OK' if result else 'NO_TABLES')
exit(0 if result else 1)
" 2>/dev/null; then
        echo -e "${GREEN}✓ Database tables exist${NC}"
        return 0
    else
        echo -e "${YELLOW}Database tables need to be created${NC}"
        return 1
    fi
}

# Function to initialize database
initialize_database() {
    echo -e "${YELLOW}Initializing database...${NC}"
    
    # Create migrations for our apps
    echo -e "${YELLOW}Creating migrations for core models...${NC}"
    python3 manage.py makemigrations core_models --noinput || echo "Core models migrations might already exist"
    
    echo -e "${YELLOW}Creating migrations for alerts app...${NC}"
    python3 manage.py makemigrations alerts_app --noinput || echo "Alerts app migrations might already exist"
    
    echo -e "${YELLOW}Creating migrations for other apps...${NC}"
    python3 manage.py makemigrations --noinput || echo "Other migrations might already exist"
    
    # Apply migrations
    if run_django_command "migrate --noinput" "Applying migrations"; then
        echo -e "${GREEN}✓ Database migration completed${NC}"
    else
        echo -e "${RED}✗ Database migration failed${NC}"
        return 1
    fi
    
    # Create superuser if needed
    echo -e "${YELLOW}Creating superuser if needed...${NC}"
    python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin@admin.com', 'admin', first_name='Admin', last_name='User', role='admin')
    print('Superuser created: admin@admin.com / admin')
else:
    print('Superuser already exists')
" || echo "Warning: Could not create superuser"
    
    return 0
}

# Main execution
main() {
    # Check if database is accessible and tables exist
    if check_database_tables; then
        echo -e "${GREEN}Database is ready!${NC}"
    else
        echo -e "${YELLOW}Database needs initialization...${NC}"
        
        if initialize_database; then
            echo -e "${GREEN}Database initialization completed!${NC}"
        else
            echo -e "${RED}Database initialization failed.${NC}"
            exit 1
        fi
    fi
    
    # Collect static files
    run_django_command "collectstatic --noinput" "Collecting static files" || echo "Warning: Static files collection failed"
    
    echo -e "${GREEN}Database setup completed successfully!${NC}"
}

# Run main function
main
