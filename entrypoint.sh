#!/bin/sh
# Script d'entrée pour le conteneur Docker

# Vérification des variables d'environnement nécessaires
: "${DATABASE:?DATABASE environment variable is required}"
: "${SQL_HOST:?SQL_HOST environment variable is required}"
: "${SQL_PORT:?SQL_PORT environment variable is required}"
: "${DJANGO_SETTINGS_MODULE:?DJANGO_SETTINGS_MODULE environment variable is required}"

# Configuration de Django
export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"
export PYTHONPATH="/code"

echo "Entrypoint script started with DATABASE=$DATABASE, SQL_HOST=$SQL_HOST, SQL_PORT=$SQL_PORT, DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Activer le mode strict pour arrêter le script en cas d'erreur
if [ -z "$DATABASE" ] || [ -z "$SQL_HOST" ] || [ -z "$SQL_PORT" ] || [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo "Error: Required environment variables are not set."
    exit 1
fi

# Vérifier si le conteneur est en mode développement ou production
if [ "$DJANGO_SETTINGS_MODULE" = "router_supervisor.src.settings.dev" ]; then
    echo "Running in development mode"
else
    echo "Running in production mode"
fi

# Activer le mode strict pour arrêter le script en cas d'erreur
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo "Error: DJANGO_SETTINGS_MODULE is not set."
    exit 1
fi

# Installer les dépendances si nécessaire
if [ ! -d "/code/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv /code/venv
fi

# Activer l'environnement virtuel
echo "Activating virtual environment..."
. /code/venv/bin/activate

# Installer les dépendances Python
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r /code/requirements.txt

# Vérifier si 'nc' est installé pour vérifier la disponibilité de PostgreSQL
if ! command -v nc >/dev/null 2>&1; then
    echo "Installing 'nc' (netcat) for checking PostgreSQL availability..."
    dnf install -y nc || apt-get install -y netcat || yum install -y nc || echo "Failed to install 'nc'."
fi
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

# Initialize database with robust error handling
echo "Running database initialization script..."
if [ -f /code/scripts/init_database.sh ]; then
    /code/scripts/init_database.sh
else
    # Fallback to old method if script is missing
    echo "Database initialization script not found, using fallback method..."
    echo "Making migrations..."
    cd /code && python3 router_supervisor/manage.py makemigrations
    
    echo "Applying migrations..."
    cd /code && python3 router_supervisor/manage.py migrate
    
    echo "Creating superuser..."
    cd /code && python3 router_supervisor/manage.py shell < router_supervisor/create_superuser.py || echo "Warning: superuser creation failed"
fi

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

# echo "Configuring Telegraf..."
# Check if a telegraf config exists in the mounted volume
# if [ -f /etc/telegraf/telegraf.conf.custom ]; then
#     echo "Using custom Telegraf config from volume"
#     cp /etc/telegraf/telegraf.conf.custom /etc/telegraf/telegraf.conf
# fi

# Ensure the telegraf config has the right permissions
#chmod 644 /etc/telegraf/telegraf.conf

#echo "Starting Telegraf..."
#telegraf --config /etc/telegraf/telegraf.conf & # start as a background process

echo "Starting pipeline data collection..."
# Create run flag for pipeline
touch /code/run.flag
# Start pipeline as background process
cd /code && python3 pipeline.py &

echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python path: $(python3 -c 'import sys; print(sys.path)')"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

# Create symlinks to simplify imports
ln -sf /code/router_supervisor/src /code/src

echo "Launching: $@"
exec "$@"