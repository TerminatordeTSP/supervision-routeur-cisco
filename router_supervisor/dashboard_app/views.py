from django.shortcuts import render # type: ignore
from api_app.influx_utils import get_influx_dashboard_context
from core_models.models import Routeur, Alertes
import json
from datetime import datetime, timedelta

def index(request):
    # Get router data from InfluxDB
    influx_context = get_influx_dashboard_context()
    
    # Get router data from PostgreSQL
    try:
        routers = Routeur.objects.all()
        recent_alerts = Alertes.objects.filter(
            date_log__gte=datetime.now() - timedelta(hours=24)
        ).order_by('-date_log')[:10]
    except Exception as e:
        routers = []
        recent_alerts = []
        print(f"Error fetching database data: {e}")
    
    # Context data for the dashboard template
    context = {
        'routers': routers,
        'alerts': recent_alerts,
        'influx_data': influx_context.get('influx_data'),
        'influx_alerts': influx_context.get('influx_alerts'),
        'influx_available': influx_context.get('influx_available', False),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return render(request, "dashboard.html", context)