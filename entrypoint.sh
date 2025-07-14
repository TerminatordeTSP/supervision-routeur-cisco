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
mkdir -p /code/static /code/media /tmp/metrics
chmod -R 755 /code/static /code/media /tmp/metrics


# Créer un fichier init dans le dossier src pour qu'il soit reconnu comme un package Python
touch /code/router_supervisor/src/__init__.py

# Nettoyer les migrations (sauf __init__.py) à chaque démarrage
if [ -f /code/scripts/clean_migrations.sh ]; then
    echo "Cleaning Django migration files..."
    /code/scripts/clean_migrations.sh
fi

echo "Checking for missing migrations..."
cd /code && python3 router_supervisor/manage.py makemigrations --check --no-input || echo "Missing migrations detected!"

echo "Applying migrations..."
cd /code && python3 router_supervisor/manage.py migrate --noinput || echo "Migration failed but continuing..."

# Collecte des fichiers statiques
echo "Collecting static files..."
cd /code && python3 router_supervisor/manage.py collectstatic --noinput || echo "Collectstatic failed but continuing..."

# Debug: Show collected static files
echo "Static files collected to:"
ls -la /code/static/
echo "CSS files found:"
find /code/static -name "*.css" -type f | sort

# system errors check
echo "Running system checks..."
cd /code && python3 router_supervisor/manage.py check --deploy || echo "System check failed but continuing..."

echo "Configuring Telegraf..."
# Check if a telegraf config exists in the mounted volume
if [ -f /etc/telegraf/telegraf.conf.custom ]; then
    echo "Using custom Telegraf config from volume"
    cp /etc/telegraf/telegraf.conf.custom /etc/telegraf/telegraf.conf
fi

# Ensure the telegraf config has the right permissions
chmod 644 /etc/telegraf/telegraf.conf

echo "Starting Telegraf..."
telegraf --config /etc/telegraf/telegraf.conf & # start as a background process

echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python path: $(python3 -c 'import sys; print(sys.path)')"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

# Create symlinks to simplify imports
ln -sf /code/router_supervisor/src /code/src

echo "Launching: $@"
exec "$@"