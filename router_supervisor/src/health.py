from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os

def health_check(request):
    """
    Health check endpoint to verify application status
    """
    health_status = {
        'status': 'ok',
        'timestamp': None,
        'database': 'unknown',
        'static_files': 'unknown',
        'environment': os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown')
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        health_status['status'] = 'warning'
    
    # Check static files
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            health_status['static_files'] = 'ok'
        else:
            health_status['static_files'] = 'missing'
    except Exception as e:
        health_status['static_files'] = f'error: {str(e)}'
    
    # Add timestamp
    from datetime import datetime
    health_status['timestamp'] = datetime.now().isoformat()
    
    return JsonResponse(health_status)
