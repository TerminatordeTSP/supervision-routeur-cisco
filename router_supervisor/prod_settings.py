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

# Configuration des fichiers média
MEDIA_ROOT = '/code/media'
MEDIA_URL = '/media/'

# Configuration de sécurité
DEBUG = False
ALLOWED_HOSTS = ['*']  # À ajuster selon vos besoins de sécurité