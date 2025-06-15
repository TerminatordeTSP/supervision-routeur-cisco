#!/bin/bash
# Script pour tester l'API Django

set -e

API_URL="http://router_django:8080/api/metrics/"
TEST_DATA_FILE="/tmp/metrics/test_data.json"

# Fonction pour les messages d'erreur
error() {
    echo "ERREUR: $1" >&2
    exit 1
}

# Vérifier si curl est installé
command -v curl >/dev/null 2>&1 || error "curl requis, veuillez l'installer"

# Créer des données de test
echo "Création de données de test..."
mkdir -p /tmp/metrics

# Générer un fichier test_data.json avec des données simulées
cat > "$TEST_DATA_FILE" <<EOF
[
  {
    "router_name": "RouterTest",
    "timestamp": "$(date +%s)",
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
  }
]
EOF

echo "Fichier de test créé: $TEST_DATA_FILE"

# Vérifier si l'API est accessible
echo "Vérification de l'API Django..."
if curl -s --head --fail "http://router_django:8080/health/" > /dev/null; then
    echo "API Django accessible"
else
    error "API Django inaccessible, veuillez vérifier si le service est en cours d'exécution"
fi

# Envoyer les données à l'API
echo "Envoi des données à l'API..."
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d @"$TEST_DATA_FILE" "$API_URL")

# Afficher la réponse
echo "Réponse de l'API:"
echo "$RESPONSE"

# Vérifier si la réponse contient "success"
if echo "$RESPONSE" | grep -q "success"; then
    echo "Test réussi! L'API a reçu les données correctement."
    exit 0
else
    error "Test échoué! L'API n'a pas répondu avec succès."
    exit 1
fi