#!/bin/bash
# Script de test pour vérifier l'installation automatique
# Utilisé pour valider que tous les services fonctionnent correctement

echo "🧪 Test de l'installation automatique"
echo "====================================="

# Fonction pour tester un service
test_service() {
    local service_name=$1
    local url=$2
    local expected_status=$3
    
    echo -n "Testing $service_name... "
    
    # Tester avec timeout
    if timeout 10 curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 20

# Tests des services
echo "🔍 Test des services..."
test_service "Django Dashboard" "http://localhost:8080/" "200"
test_service "Django Health" "http://localhost:8080/health/" "200"
test_service "Django API Metrics" "http://localhost:8080/api/latest-metrics/" "200"
test_service "Django Settings" "http://localhost:8080/settings/" "200"
test_service "InfluxDB" "http://localhost:8086/health" "200"
test_service "pgAdmin" "http://localhost:5050/" "200"

# Test de la base de données
echo "🗄️  Test de la base de données..."
if docker-compose exec -T router_django python3 router_supervisor/manage.py check > /dev/null 2>&1; then
    echo "✅ Base de données OK"
else
    echo "❌ Problème avec la base de données"
fi

# Test des migrations
echo "📦 Test des migrations..."
if docker-compose exec -T router_django python3 router_supervisor/manage.py showmigrations --plan > /dev/null 2>&1; then
    echo "✅ Migrations OK"
else
    echo "❌ Problème avec les migrations"
fi

# Test du superutilisateur
echo "👤 Test du superutilisateur..."
if docker-compose exec -T router_django python3 router_supervisor/manage.py shell -c "from django.contrib.auth.models import User; print('✅ Superuser exists' if User.objects.filter(username='admin').exists() else '❌ No superuser')" 2>/dev/null; then
    echo "✅ Superutilisateur OK"
else
    echo "❌ Problème avec le superutilisateur"
fi

# Résumé des statuts
echo ""
echo "📊 Résumé des statuts des conteneurs:"
docker-compose ps

echo ""
echo "🎯 Test terminé!"
echo "Si tous les tests sont OK, l'installation automatique fonctionne correctement."
