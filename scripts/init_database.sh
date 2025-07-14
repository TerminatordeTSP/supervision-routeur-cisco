#!/bin/bash

# Database initialization and health check script
# This script ensures the database is properly set up before starting the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database initialization and health check...${NC}"

# Change to the router_supervisor directory
cd /code/router_supervisor

# Function to run Django management commands with proper error handling
run_django_command() {
    local command="$1"
    local description="$2"
    
    echo -e "${YELLOW}$description${NC}"
    
    if python3 manage.py "$command"; then
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
    
    if python3 manage.py dbhealth > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database health check passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Database health check failed${NC}"
        return 1
    fi
}

# Function to initialize database
initialize_database() {
    echo -e "${YELLOW}Initializing database...${NC}"
    
    # Try the custom initialize_db command first
    if run_django_command "initialize_db --max-retries=30" "Database initialization"; then
        return 0
    fi
    
    # Fallback to manual migration
    echo -e "${YELLOW}Falling back to manual migration...${NC}"
    
    # Create migrations if needed
    run_django_command "makemigrations --no-input" "Creating migrations" || true
    
    # Apply migrations
    if run_django_command "migrate --no-input" "Applying migrations"; then
        return 0
    else
        echo -e "${RED}Database initialization failed completely${NC}"
        return 1
    fi
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
            echo -e "${RED}Database initialization failed. The application may not work correctly.${NC}"
            exit 1
        fi
    fi
    
    # Final health check
    run_django_command "dbhealth" "Final database health check" || true
    
    # Collect static files
    run_django_command "collectstatic --no-input" "Collecting static files" || true
    
    echo -e "${GREEN}Database setup completed successfully!${NC}"
}

# Run main function
main
