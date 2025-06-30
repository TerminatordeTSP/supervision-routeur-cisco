#!/bin/bash

# Script de déploiement pour supervision-routeur-cisco
# Ce script déploie l'application sur un serveur distant

set -e

# Variables de configuration
SERVER_HOST="supervision-server"  # Utilise la config SSH
REMOTE_PATH="/opt/supervision-routeur-cisco"
REMOTE_USER="$(ssh -G $SERVER_HOST | awk '/^user / {print $2}')"
APP_NAME="supervision-routeur-cisco"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier que git est propre
check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        log_warning "Des fichiers non commités détectés. Veuillez commiter vos changements avant de déployer."
        git status --short
        read -p "Continuer quand même ? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Vérifier la connexion SSH
check_ssh_connection() {
    log_info "Test de la connexion SSH vers $SERVER_HOST..."
    if ssh -o ConnectTimeout=10 "$SERVER_HOST" "echo 'Connexion SSH OK'" > /dev/null 2>&1; then
        log_success "Connexion SSH établie"
    else
        log_error "Impossible de se connecter à $SERVER_HOST"
        log_info "Vérifiez votre configuration SSH et assurez-vous que le serveur est accessible"
        exit 1
    fi
}

# Préparer le serveur distant
prepare_remote_server() {
    log_info "Préparation du serveur distant..."
    
    # Créer les répertoires nécessaires
    ssh "$SERVER_HOST" "sudo mkdir -p $REMOTE_PATH && sudo chown $REMOTE_USER:$REMOTE_USER $REMOTE_PATH"
    
    # Installer Docker si nécessaire
    ssh "$SERVER_HOST" "
        if ! command -v docker &> /dev/null; then
            echo 'Installation de Docker...'
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $REMOTE_USER
            rm get-docker.sh
        fi
        
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo 'Installation de Docker Compose...'
            sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
        fi
    "
    
    log_success "Serveur distant préparé"
}

# Synchroniser les fichiers
sync_files() {
    log_info "Synchronisation des fichiers..."
    
    # Exclure les fichiers/dossiers non nécessaires
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
    
    log_success "Fichiers synchronisés"
}

# Déployer l'application
deploy_application() {
    log_info "Déploiement de l'application..."
    
    ssh "$SERVER_HOST" "
        cd $REMOTE_PATH
        
        # Arrêter les conteneurs existants
        if [[ -f docker-compose.yml ]]; then
            docker compose down --remove-orphans || true
        fi
        
        # Construire et démarrer les nouveaux conteneurs
        docker compose build --no-cache
        docker compose up -d
        
        # Attendre que les services soient prêts
        echo 'Attente du démarrage des services...'
        sleep 30
        
        # Vérifier le statut
        docker compose ps
    "
    
    log_success "Application déployée"
}

# Vérifier le déploiement
verify_deployment() {
    log_info "Vérification du déploiement..."
    
    # Tester les ports principaux
    ssh "$SERVER_HOST" "
        # Test Django (port 80 via Caddy)
        if curl -f -s http://localhost/ > /dev/null; then
            echo '✅ Application web accessible'
        else
            echo '❌ Application web non accessible'
        fi
        
        # Test InfluxDB
        if curl -f -s http://localhost:8086/ping > /dev/null; then
            echo '✅ InfluxDB accessible'
        else
            echo '❌ InfluxDB non accessible'
        fi
        
        # Test PgAdmin
        if curl -f -s http://localhost:5050/ > /dev/null; then
            echo '✅ PgAdmin accessible'
        else
            echo '❌ PgAdmin non accessible'
        fi
    "
    
    log_success "Vérification terminée"
}

# Afficher les informations post-déploiement
show_deployment_info() {
    log_success "🚀 Déploiement terminé!"
    echo ""
    log_info "Services disponibles:"
    ssh "$SERVER_HOST" "
        SERVER_IP=\$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print \$1}')
        echo \"  📊 Application web: http://\$SERVER_IP/\"
        echo \"  📈 InfluxDB: http://\$SERVER_IP:8086/\"
        echo \"  🐘 PgAdmin: http://\$SERVER_IP:5050/\"
        echo \"\"
        echo \"📋 Statut des conteneurs:\"
        cd $REMOTE_PATH && docker compose ps
    "
}

# Menu principal
main() {
    echo "🚀 Script de déploiement - Supervision Routeur Cisco"
    echo "=================================================="
    
    case "${1:-}" in
        --prepare-only)
            check_ssh_connection
            prepare_remote_server
            ;;
        --sync-only)
            check_ssh_connection
            sync_files
            ;;
        --deploy-only)
            check_ssh_connection
            deploy_application
            verify_deployment
            show_deployment_info
            ;;
        *)
            check_git_status
            check_ssh_connection
            prepare_remote_server
            sync_files
            deploy_application
            verify_deployment
            show_deployment_info
            ;;
    esac
}

# Gestion des erreurs
trap 'log_error "Erreur lors du déploiement à la ligne $LINENO"' ERR

# Exécution
main "$@"
