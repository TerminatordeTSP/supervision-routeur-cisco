#!/bin/bash
# Script de démarrage rapide pour développeurs
# Pour les utilisateurs qui veulent juste démarrer le projet rapidement

echo "🚀 Démarrage rapide du projet de supervision Routeur Cisco"
echo "=========================================================="

# Vérification rapide des prérequis
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker ou Docker Compose non installé"
    exit 1
fi

# Arrêter les anciens conteneurs
echo "🛑 Arrêt des anciens conteneurs..."
docker-compose down -v 2>/dev/null || true

# Démarrage avec build automatique
echo "🔨 Construction et démarrage..."
docker-compose up --build -d

# Attendre un peu
echo "⏳ Attente de stabilisation..."
sleep 15

# Vérifier le statut
echo "📊 Statut des services:"
docker-compose ps

# Vérifier la santé du service principal
echo "🏥 Vérification de la santé des services..."
if curl -s http://localhost:8080/health/ > /dev/null; then
    echo "✅ Service Django opérationnel"
else
    echo "⚠️  Service Django en cours de démarrage..."
fi

echo ""
echo "🎉 Démarrage terminé!"
echo "Dashboard: http://localhost:8080/"
echo "Admin: admin/admin123"
echo ""
echo "Commandes utiles:"
echo "  Logs:     docker-compose logs -f"
echo "  Arrêter:  docker-compose down"
echo "  Rebuild:  docker-compose up --build"
