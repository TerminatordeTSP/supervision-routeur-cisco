#!/bin/bash

# Script pour exécuter le collecteur sans dépendance Django/PostgreSQL
# Utile en cas de problème avec la base de données PostgreSQL

echo "✅ Démarrage du collecteur en mode autonome (InfluxDB uniquement)"

# Créer le flag d'exécution si nécessaire
touch run.flag

# Active l'environnement virtuel s'il existe
if [ -d ".env" ]; then
    source .env/bin/activate
fi

# Installer les dépendances minimales
pip install influxdb-client

# Exécuter le collecteur (qui détectera automatiquement l'absence de Django)
python collect_metrics.py

echo "📊 Le collecteur s'est arrêté"
