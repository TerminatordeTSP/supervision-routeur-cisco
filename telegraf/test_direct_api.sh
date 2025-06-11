#!/bin/bash
# Script pour tester directement l'API Django avec le format exact attendu

set -e

API_URL="${1:-http://router_django:8080/api/metrics/}"
HEALTH_URL="${2:-http://router_django:8080/health/}"
TEST_DATA_FILE="/tmp/metrics/direct_test.json"

# Fonction pour les messages d'erreur
error() {
    echo "ERREUR: $1" >&2
    exit 1
}

# Vérifier si curl est installé
command -v curl >/dev/null 2>&1 || error "curl requis, veuillez l'installer"
command -v jq >/dev/null 2>&1 || echo "jq non trouvé, les réponses ne seront pas formatées"

# Créer des données de test au format exact attendu par l'API
echo "Création de données de test..."
mkdir -p /tmp/metrics

# Créer un timestamp actuel
TIMESTAMP=$(date +%s)

# Générer un fichier test_data.json avec des données au format attendu
cat > "$TEST_DATA_FILE" <<EOF
[
  {
    "router_name": "RouterTest1",
    "timestamp": "$TIMESTAMP",
    "router_metrics": {
      "cpu_usage": 42.5,
      "memory_usage": 75.3,
      "traffic_mbps": 150.8,
      "interfaces": [
        {
          "name": "GigabitEthernet0/0",
          "status": "up",
          "bandwidth": 1000,
          "input_rate": 450.6,
          "output_rate": 380.2,
          "errors": 0
        }
      ]
    }
  },
  {
    "router_name": "RouterTest2",
    "timestamp": "$TIMESTAMP",
    "router_metrics": {
      "cpu_usage": 31.8,
      "memory_usage": 64.2,
      "traffic_mbps": 98.3
    }
  }
]
EOF

echo "Fichier de test créé: $TEST_DATA_FILE"
echo "Contenu du fichier de test:"
cat "$TEST_DATA_FILE"

# Vérifier si l'API est accessible
echo -e "\nVérification de l'API Django..."
if curl -s --head --fail "$HEALTH_URL" > /dev/null; then
    echo "API Django accessible"
else
    error "API Django inaccessible, veuillez vérifier si le service est en cours d'exécution"
fi

# Envoyer les données à l'API
echo -e "\nEnvoi des données à l'API..."
if command -v jq >/dev/null 2>&1; then
    RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d @"$TEST_DATA_FILE" "$API_URL" | jq .)
else
    RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d @"$TEST_DATA_FILE" "$API_URL")
fi

# Afficher la réponse
echo -e "\nRéponse de l'API:"
echo "$RESPONSE"

# Vérifier si la réponse contient "success"
if echo "$RESPONSE" | grep -q "success"; then
    echo -e "\nTest réussi! L'API a reçu les données correctement."
    exit 0
else
    error "Test échoué! L'API n'a pas répondu avec succès."
    exit 1
fi