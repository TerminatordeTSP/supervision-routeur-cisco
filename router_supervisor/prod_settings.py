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
DEBUG = True  # Enable for direct access to port 8080
ALLOWED_HOSTS = ['*']  # À ajuster selon vos besoins de sécurité