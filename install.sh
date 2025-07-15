#!/bin/bash
# Script d'installation automatique pour le projet de supervision Routeur Cisco
# Auteur: Votre équipe
# Version: 1.0

echo "🚀 Installation automatique du projet de supervision Routeur Cisco"
echo "=================================================================="

# Vérification des prérequis
check_requirements() {
    echo "🔍 Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé. Veuillez installer Docker first."
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose first."
        exit 1
    fi
    
    echo "✅ Docker et Docker Compose sont installés"
}

# Fonction pour nettoyer les anciens conteneurs
cleanup_old_containers() {
    echo "🧹 Nettoyage des anciens conteneurs..."
    
    # Arrêter tous les conteneurs du projet
    docker-compose down -v 2>/dev/null || true
    
    # Nettoyer les images orphelines
    docker system prune -f
    
    echo "✅ Nettoyage terminé"
}

# Fonction pour créer les répertoires nécessaires
create_directories() {
    echo "📁 Création des répertoires nécessaires..."
    
    mkdir -p static media tmp/metrics
    chmod -R 755 static media tmp
    
    echo "✅ Répertoires créés"
}

# Fonction pour configurer les variables d'environnement
setup_environment() {
    echo "⚙️  Configuration des variables d'environnement..."
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f .env ]; then
        cat > .env << EOF
# Configuration de la base de données
DATABASE=postgres
SQL_HOST=postgres
SQL_PORT=5432
POSTGRES_DB=router_supervision
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Configuration Django
DJANGO_SETTINGS_MODULE=router_supervisor.src.settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True

# Configuration InfluxDB
INFLUXDB_V2_URL=http://influxdb:8086
INFLUXDB_V2_ORG=router_supervision
INFLUXDB_V2_BUCKET=router_metrics
INFLUXDB_V2_TOKEN=your-influxdb-token

# Configuration réseau
ROUTER_IP=192.168.1.1
SNMP_COMMUNITY=public
SNMP_PORT=161
EOF
        echo "✅ Fichier .env créé avec les valeurs par défaut"
    else
        echo "ℹ️  Fichier .env existant conservé"
    fi
}

# Fonction principale d'installation
main_installation() {
    echo "🔨 Construction et démarrage des services..."
    
    # Construire les images
    echo "📦 Construction des images Docker..."
    docker-compose build --no-cache
    
    # Démarrer les services
    echo "🚀 Démarrage des services..."
    docker-compose up -d
    
    # Attendre que les services soient prêts
    echo "⏳ Attente que les services soient prêts..."
    sleep 30
    
    # Vérifier le statut
    echo "📊 Vérification du statut des services..."
    docker-compose ps
}

# Fonction pour afficher les informations finales
show_final_info() {
    echo ""
    echo "🎉 Installation terminée avec succès!"
    echo "====================================="
    echo ""
    echo "🌐 Accès aux services:"
    echo "  Dashboard:    http://localhost:8080/"
    echo "  Settings:     http://localhost:8080/settings/"
    echo "  Alertes:      http://localhost:8080/alertes/"
    echo "  Thresholds:   http://localhost:8080/thresholds/"
    echo "  InfluxDB:     http://localhost:8086/"
    echo "  pgAdmin:      http://localhost:5050/"
    echo ""
    echo "👤 Compte administrateur:"
    echo "  Utilisateur:  admin"
    echo "  Mot de passe: admin123"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "  Arrêter:      docker-compose down"
    echo "  Redémarrer:   docker-compose restart"
    echo "  Logs:         docker-compose logs -f"
    echo "  Reconstruire: docker-compose up --build"
    echo ""
    echo "📚 Documentation complète disponible dans le README.md"
}

# Fonction pour gérer les erreurs
handle_error() {
    echo "❌ Erreur détectée pendant l'installation!"
    echo "Consultez les logs ci-dessus pour plus d'informations."
    echo "Tentative de nettoyage..."
    docker-compose down -v
    exit 1
}

# Piège pour gérer les erreurs
trap handle_error ERR

# Exécution du script principal
main() {
    echo "Début de l'installation..."
    check_requirements
    cleanup_old_containers
    create_directories
    setup_environment
    main_installation
    show_final_info
    
    echo "✅ Installation réussie! Votre projet est maintenant prêt à utiliser."
}

# Lancer l'installation
main "$@"
