from django.shortcuts import render # type: ignore
from api_app.influx_utils import get_influx_dashboard_context
# from router_supervisor.core_models.models import Routeur, Alertes  # Désactivé temporairement
import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .influx_utils import get_latest_cpu_usage, get_latest_ram_usage, get_latest_octets
from django.http import JsonResponse
from influxdb_client import InfluxDBClient
from django.views.decorators.csrf import csrf_exempt
@login_required
def index(request):
    # Get router data from InfluxDB
    influx_context = get_influx_dashboard_context()

    # Temporairement désactivé - Get router data from PostgreSQL
    # try:
    #     routers = Routeur.objects.all()
    #     recent_alerts = Alertes.objects.filter(
    #         date_log__gte=datetime.now() - timedelta(hours=24)
    #     ).order_by('-date_log')[:10]
    # except Exception as e:
    #     routers = []
    #     recent_alerts = []
    #     print(f"Error fetching database data: {e}")

    # Données temporaires pour le test
    routers = []
    recent_alerts = []

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



def dashboard_view(request):
    cpu, cpu_time = get_latest_metric("snmp", "cpu_5min")
    ram, ram_time = get_latest_metric("mem", "used_percent")
    latency, latency_time = get_latest_metric("ping_latency", "value")
    system_load, _ = get_latest_metric("system", "load1")
    uptime, _ = get_latest_metric("system", "uptime")
    system_cpu, _ = get_latest_metric("cpu-total", "usage_user")

    context = {
        "router_cpu": cpu,
        "ram_usage": ram,
        "latency": latency,
        "system_load": system_load,
        "uptime": uptime,
        "system_cpu": system_cpu,
        "last_update": cpu_time or ram_time or latency_time,
    }
    return render(request, "dashboard_app/dashboard.html", context)


def dashboard_view(request):
    cpu_usage = get_latest_cpu_usage()
    ram_usage = get_latest_ram_usage()
    in_octets = get_latest_octets("GigabitEthernet1/4", direction="in")
    out_octets = get_latest_octets("GigabitEthernet1/4", direction="out")
    # Tu peux dupliquer pour plusieurs interfaces, ou boucler si besoin

    context = {
        "router_cpu": cpu_usage,
        "ram_usage": ram_usage,
        "in_octets": in_octets,
        "out_octets": out_octets,
        # Ajoute d’autres variables ici si tu veux afficher plus d’infos
    }
    return render(request, "dashboard_app/dashboard.html", context)

from django.http import JsonResponse
from .influx_utils import (
    get_latest_cpu_usage,
    get_latest_ram_usage,
    get_latest_latency,
    get_latest_system_load,
    get_latest_system_cpu,
    get_latest_uptime,
    get_router_name,
)

def latest_metrics_api(request):
    data = {
        "cpu_5min": get_latest_cpu_usage(),
        "ram_used": get_latest_ram_usage(),  # pourcentage
        "latency_ms": get_latest_latency(),
        "load1": get_latest_system_load(),
        "system_cpu": get_latest_system_cpu(),
        "uptime": get_latest_uptime(),   # en secondes
        "used_percent": get_latest_ram_usage(),
        "router_name": get_router_name(),
    }
    return JsonResponse(data)

INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

@csrf_exempt  # (désactive temporairement le CSRF pour tester)
def get_latest_metrics(request):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1m)
          |> last()
    '''
    result = query_api.query(org=INFLUX_ORG, query=query)
    data = []
    for table in result:
        for record in table.records:
            data.append({
                "measurement": record.get_measurement(),
                "field": record.get_field(),
                "value": record.get_value(),
                "time": str(record.get_time()),
                "tags": record.values
            })
    client.close()
    return JsonResponse(data, safe=False)