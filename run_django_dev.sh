#!/bin/bash
# Script pour lancer Django en mode développement

set -e

# Configurer les variables d'environnement
export DJANGO_SETTINGS_MODULE="router_supervisor.src.settings"
export PYTHONPATH="$(pwd)"

# Vérifier l'existence d'un environnement virtuel Python
if [ -d "env" ]; then
    echo "Activation de l'environnement virtuel (env)"
    source env/bin/activate
elif [ -d "venv" ]; then
    echo "Activation de l'environnement virtuel (venv)"
    source venv/bin/activate
else
    echo "Aucun environnement virtuel trouvé. Création d'un nouvel environnement 'venv'..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Vérifier si des migrations sont nécessaires
echo "Vérification des migrations..."
python router_supervisor/manage.py makemigrations
python router_supervisor/manage.py migrate

# Collecter les fichiers statiques (optionnel en mode dev)
# python router_supervisor/manage.py collectstatic --noinput

# Démarrer le serveur Django
echo "Démarrage du serveur Django..."
python router_supervisor/manage.py runserver 0.0.0.0:8000