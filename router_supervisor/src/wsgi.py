"""
WSGI config for router_supervisor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.core.wsgi import get_wsgi_application # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'router_supervisor.prod_settings')

application = get_wsgi_application()
