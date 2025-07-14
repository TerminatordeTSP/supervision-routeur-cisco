#!/bin/bash
# Docker Management Script for Router Supervisor
# This script helps manage the Docker environment

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

show_help() {
    echo "Router Supervisor Docker Management"
    echo "=================================="
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build         Build the Docker containers"
    echo "  up            Start the services"
    echo "  down          Stop the services"
    echo "  restart       Restart the services"
    echo "  logs          Show logs"
    echo "  shell         Open shell in Django container"
    echo "  install       Run installation script"
    echo "  reset         Reset database and volumes"
    echo "  status        Show service status"
    echo "  help          Show this help message"
}

build_containers() {
    print_status "Building Docker containers..."
    docker-compose build --no-cache
    print_success "Containers built successfully!"
}

start_services() {
    print_status "Starting services..."
    docker-compose up -d
    print_success "Services started!"
    
    echo ""
    print_status "Waiting for services to be healthy..."
    sleep 10
    
    echo ""
    print_status "Service URLs:"
    echo "  🌐 Main Application: http://localhost/"
    echo "  ⚙️  Admin Panel: http://localhost/admin/"
    echo "  🗄️  PgAdmin: http://localhost:5050/"
    echo "  📊 Direct Django: http://localhost:8080/"
}

stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped!"
}

restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_success "Services restarted!"
}

show_logs() {
    if [ -n "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f
    fi
}

open_shell() {
    print_status "Opening shell in Django container..."
    docker-compose exec router_django /bin/bash
}

run_install() {
    print_status "Running installation script..."
    docker-compose exec router_django /code/scripts/install.sh
}

reset_database() {
    print_warning "This will delete all data! Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Stopping services..."
        docker-compose down
        
        print_status "Removing volumes..."
        docker volume rm supervision-routeur-cisco_pgdata 2>/dev/null || true
        
        print_status "Removing installation flag..."
        docker-compose run --rm router_django rm -f /code/.installation_complete
        
        print_status "Starting fresh..."
        docker-compose up -d
        
        print_success "Database reset complete!"
    else
        print_status "Reset cancelled."
    fi
}

show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Container Health:"
    docker-compose exec router_django curl -s http://localhost:8080/health/ || print_warning "Django health check failed"
    
    echo ""
    print_status "Database Status:"
    docker-compose exec db pg_isready -U user -d routerdb || print_warning "Database not ready"
}

# Main script logic
case "${1:-help}" in
    build)
        build_containers
        ;;
    up|start)
        start_services
        ;;
    down|stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs "$@"
        ;;
    shell|bash)
        open_shell
        ;;
    install)
        run_install
        ;;
    reset)
        reset_database
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
