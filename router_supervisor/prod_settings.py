from src.settings import *
import os

# Configuration de la base de données pour la production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SQL_DATABASE', 'routerdb'),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'db'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}

# Override INSTALLED_APPS to ensure alerts_app is properly configured
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'router_supervisor.core_models.apps.CoreModelsConfig',
    'router_supervisor.settings_app',
    'router_supervisor.dashboard_app',
    'router_supervisor.thresholds_app',
    'router_supervisor.alerts_app.apps.AlertsAppConfig',
    'router_supervisor.api_app',
]

# Configuration des fichiers statiques
STATIC_ROOT = '/code/static'
STATIC_URL = '/static/'

# Include STATICFILES_DIRS for proper static file collection
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'dashboard_app/static'),
    os.path.join(BASE_DIR, 'settings_app/static'),
    os.path.join(BASE_DIR, 'thresholds_app/static'),
]

# Configuration des fichiers média
MEDIA_ROOT = '/code/media'
MEDIA_URL = '/media/'

# Configuration de sécurité
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')
ALLOWED_HOSTS = ['*']  # À ajuster selon vos besoins de sécurité

# Configuration pour servir les fichiers statiques en production
# Ajouter whitenoise au middleware pour servir les fichiers statiques
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Ajouter pour servir les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration Whitenoise pour les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'