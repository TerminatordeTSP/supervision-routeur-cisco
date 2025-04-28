#!/bin/sh
set -e

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for PostgreSQL at $SQL_HOST:$SQL_PORT..."
    
    # Vérifier si nc est installé
    if ! command -v nc >/dev/null 2>&1; then
        echo "Error: 'nc' command not found. Installing..."
        dnf install -y nc
    fi
    
    # Compteur pour limiter les tentatives
    counter=0
    max_tries=60
    
    # Boucle avec limite d'essais
    while ! nc -z $SQL_HOST $SQL_PORT; do
        counter=$((counter+1))
        if [ $counter -ge $max_tries ]; then
            echo "Error: PostgreSQL not available after $max_tries attempts. Continuing anyway..."
            break
        fi
        echo "Waiting for PostgreSQL... (attempt $counter/$max_tries)"
        sleep 1
    done
    
    if [ $counter -lt $max_tries ]; then
        echo "PostgreSQL started successfully!"
    fi
    
    # Petit délai supplémentaire pour s'assurer que PostgreSQL est bien prêt
    sleep 2
fi

# Vérification des variables d'environnement
echo "Environment variables:"
echo "DATABASE: $DATABASE"
echo "SQL_HOST: $SQL_HOST"
echo "SQL_PORT: $SQL_PORT"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# S'assurer que les répertoires statiques et média existent
mkdir -p /code/static /code/media
chmod -R 755 /code/static /code/media

# Exécuter les migrations Django automatiquement
echo "Applying migrations..."
python3 manage.py migrate --noinput || echo "Migration failed but continuing..."

# Collecte des fichiers statiques
echo "Collecting static files..."
python3 manage.py collectstatic --noinput || echo "Collectstatic failed but continuing..."

# Exécution des vérifications du système
echo "Running system checks..."
python3 manage.py check || echo "System check failed but continuing..."

# Démarrer Telegraf en arrière-plan
echo "Starting Telegraf..."
telegraf --config /etc/telegraf/telegraf.conf &

# Après le démarrage de Telegraf
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python path: $(python3 -c 'import sys; print(sys.path)')"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

# Afficher la commande qui va être exécutée
echo "Launching: $@"
exec "$@"

mkdir -p /code/src
mv /code/prod_settings.py /code/src/