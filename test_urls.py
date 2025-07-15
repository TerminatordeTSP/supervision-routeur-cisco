#!/usr/bin/env python3
import os
import sys
import django

# Configuration du chemin Django
sys.path.insert(0, '/code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# Initialiser Django
django.setup()

from django.urls import get_resolver, reverse

try:
    # Tester l'URL reverse
    url = reverse('interfaces_api')
    print(f"URL reverse pour 'interfaces_api': {url}")
except Exception as e:
    print(f"Erreur lors du reverse: {e}")

# Lister les patterns disponibles
resolver = get_resolver()
print("\nPatterns disponibles:")
for pattern in resolver.url_patterns:
    print(f"  {pattern}")
