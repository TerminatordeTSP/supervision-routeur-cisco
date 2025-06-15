#!/bin/bash
set -e

# Configuration de base
echo "Starting Telegraf initialization..."
mkdir -p /tmp/metrics /var/log/telegraf
chmod -R 755 /tmp/metrics /var/log/telegraf

# Vérifier que le fichier de configuration existe
if [ ! -f /etc/telegraf/telegraf.conf ]; then
    echo "ERREUR: Fichier telegraf.conf manquant!"
    exit 1
fi

echo "Configurations chargées avec succès"

# Générer quelques données test simples directement
echo "Génération de données test initiales..."
echo '[
  {
    "router_name": "Router_Sample",
    "timestamp": "'$(date +%s)'",
    "router_metrics": {
      "cpu_usage": 30,
      "memory_usage": 50,
      "traffic_mbps": 100
    }
  }
]' > /tmp/metrics/initial_data.json

echo "Données test générées: /tmp/metrics/initial_data.json"

# Essayer de contacter le service Django en arrière-plan
(
    # Attendre que le service soit disponible (10 tentatives max)
    retries=10
    while [ $retries -gt 0 ]; do
        if curl -s --head --fail http://router_django:8080/health/ > /dev/null 2>&1; then
            echo "Service Django disponible, envoi des données test..."
            curl -s -X POST -H "Content-Type: application/json" -d @/tmp/metrics/initial_data.json \
                 http://router_django:8080/api/metrics/ || echo "Erreur lors de l'envoi des données"
            break
        fi
        retries=$((retries-1))
        echo "En attente du service Django... ($retries tentatives restantes)"
        sleep 5
    done
) &

echo "Initialisation Telegraf terminée, démarrage du service..."

# Démarrer Telegraf en premier plan avec toutes les options passées
exec telegraf --config /etc/telegraf/telegraf.conf