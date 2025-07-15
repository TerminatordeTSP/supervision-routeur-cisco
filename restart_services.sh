#!/bin/bash
# Script pour redémarrer les services et appliquer les modifications

echo "🔄 Redémarrage des services de supervision..."

# Arrêter les conteneurs
echo "⏹️  Arrêt des conteneurs..."
docker-compose down

# Nettoyer les images si nécessaire
echo "🧹 Nettoyage des images..."
docker system prune -f

# Reconstruire les images
echo "🔨 Reconstruction des images..."
docker-compose build --no-cache

# Redémarrer les services
echo "▶️  Redémarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 30

# Vérifier le statut
echo "📊 Vérification du statut..."
docker-compose ps

# Afficher les logs récents
echo "📋 Logs récents de Telegraf:"
docker logs telegraf --tail 20

echo "📋 Logs récents de Django:"
docker logs router_django --tail 10

echo "✅ Services redémarrés avec succès!"
echo "🌐 Dashboard disponible sur: http://localhost:8080/"
echo "📊 InfluxDB disponible sur: http://localhost:8086/"
echo "🔧 pgAdmin disponible sur: http://localhost:5050/"
