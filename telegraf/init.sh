#!/bin/bash
set -e

# Script d'initialisation pour Telegraf

# Création des répertoires nécessaires
mkdir -p /tmp/metrics
mkdir -p /var/log/telegraf

# Configurer les permissions appropriées
chmod -R 755 /tmp/metrics
chmod -R 755 /var/log/telegraf

# Vérifier que les fichiers de configuration sont présents
if [ ! -f /etc/telegraf/telegraf.conf ]; then
    echo "Fichier telegraf.conf manquant!"
    exit 1
fi

echo "Configuration Telegraf:"
cat /etc/telegraf/telegraf.conf

# Copier les scripts utilitaires dans un emplacement accessible
cp /etc/telegraf/generate_test_data.py /tmp/metrics/ 2>/dev/null || echo "generate_test_data.py non trouvé"
cp /etc/telegraf/send_test_data.py /tmp/metrics/ 2>/dev/null || echo "send_test_data.py non trouvé"
chmod +x /tmp/metrics/*.py 2>/dev/null

# Vérifier la connectivité avec router_django
echo "Vérification de la connexion à router_django..."
timeout 5 bash -c 'until nc -z router_django 8080; do sleep 0.5; done' || echo "Attention: router_django n'est pas encore disponible"

# Générer quelques données test pour démarrer
if [ -f /tmp/metrics/generate_test_data.py ]; then
    echo "Génération de données test initiales..."
    /tmp/metrics/generate_test_data.py --output /tmp/metrics/initial_data.json
fi

echo "Initialisation Telegraf terminée"

# Lancer Telegraf avec la bonne configuration
exec telegraf --config /etc/telegraf/telegraf.conf