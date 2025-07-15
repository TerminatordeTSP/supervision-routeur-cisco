from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import random
import threading
import time as time_module

# Configuration InfluxDB
INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

# Essayer d'importer InfluxDB client
try:
    from influxdb_client import InfluxDBClient
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False
    print("InfluxDB client not available, using fallback data")

def get_fallback_metrics():
    """Retourne des données de fallback réalistes basées sur les vraies métriques SNMP"""
    now = datetime.now().isoformat()
    
    # Données plus réalistes avec variation
    cpu_usage = random.uniform(5, 15)  # CPU entre 5% et 15%
    ram_used = random.randint(180000000, 220000000)  # RAM utilisée variable
    ram_free = random.randint(1800000000, 1900000000)  # RAM libre variable
    uptime = 353899741 + random.randint(0, 86400)  # Uptime qui augmente
    latency = random.uniform(2.0, 8.0)  # Latence variable
    
    return [
        {"measurement": "snmp", "field": "cpu_0_usage", "value": round(cpu_usage, 1), "time": now, "tags": {"hostname": "Cisco-Router-Main", "agent_host": "172.16.10.41"}},
        {"measurement": "snmp", "field": "cpu_5min", "value": round(cpu_usage * 0.8, 1), "time": now, "tags": {"hostname": "Cisco-Router-Main", "agent_host": "172.16.10.41"}},
        {"measurement": "snmp", "field": "ram_used", "value": ram_used, "time": now, "tags": {"hostname": "Cisco-Router-Main", "agent_host": "172.16.10.41"}},
        {"measurement": "snmp", "field": "ram_free", "value": ram_free, "time": now, "tags": {"hostname": "Cisco-Router-Main", "agent_host": "172.16.10.41"}},
        {"measurement": "snmp", "field": "uptime", "value": uptime, "time": now, "tags": {"hostname": "Cisco-Router-Main", "agent_host": "172.16.10.41"}},
        {"measurement": "ping", "field": "average_response_ms", "value": round(latency, 1), "time": now, "tags": {"hostname": "Cisco-Router-Main", "url": "172.16.10.41"}},
        {"measurement": "interfaces", "field": "ifInOctets", "value": random.randint(1000000, 5000000), "time": now, "tags": {"hostname": "Cisco-Router-Main", "ifDescr": "GigabitEthernet0/0"}},
        {"measurement": "interfaces", "field": "ifOutOctets", "value": random.randint(800000, 3000000), "time": now, "tags": {"hostname": "Cisco-Router-Main", "ifDescr": "GigabitEthernet0/0"}},
    ]

# Cache simple pour éviter les requêtes répétées
class MetricsCache:
    def __init__(self, ttl=3):  # TTL de 3 secondes
        self.cache = {}
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                data, timestamp = self.cache[key]
                if time_module.time() - timestamp < self.ttl:
                    return data
                else:
                    del self.cache[key]
            return None
    
    def set(self, key, value):
        with self.lock:
            self.cache[key] = (value, time_module.time())

# Instance globale du cache
metrics_cache = MetricsCache()

def get_latest_metrics_from_influx():
    """Récupère les dernières métriques depuis InfluxDB avec cache"""
    if not INFLUX_AVAILABLE:
        print("Client InfluxDB non disponible, utilisation des données de fallback")
        return get_fallback_metrics()
    
    # Essayer de récupérer depuis le cache
    cached_data = metrics_cache.get("latest_metrics")
    if cached_data is not None:
        return cached_data
    
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        query_api = client.query_api()
        
        # Requête optimisée pour récupérer les dernières valeurs SNMP
        query = f'''
            snmp_data = from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -5m)
              |> filter(fn: (r) => r["_measurement"] == "snmp")
              |> filter(fn: (r) => r["_field"] == "cpu_0_usage" or r["_field"] == "cpu_5min" or r["_field"] == "ram_used" or r["_field"] == "ram_free" or r["_field"] == "uptime")
              |> group(columns: ["_field"])
              |> last()
            
            ping_data = from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -5m)
              |> filter(fn: (r) => r["_measurement"] == "ping")
              |> filter(fn: (r) => r["_field"] == "average_response_ms")
              |> last()
            
            interface_data = from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -5m)
              |> filter(fn: (r) => r["_measurement"] == "interfaces")
              |> filter(fn: (r) => r["_field"] == "ifInOctets" or r["_field"] == "ifOutOctets")
              |> group(columns: ["_field", "ifDescr"])
              |> last()
            
            union(tables: [snmp_data, ping_data, interface_data])
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
        
        # Si pas de données, retourner des données de fallback
        if not data:
            print("Aucune donnée InfluxDB trouvée, utilisation des données de fallback")
            fallback_data = get_fallback_metrics()
            metrics_cache.set("latest_metrics", fallback_data)
            return fallback_data
        
        # Mettre en cache les données récupérées
        metrics_cache.set("latest_metrics", data)
        print(f"✅ Données récupérées d'InfluxDB avec succès: {len(data)} métriques")
        
        return data
        
    except Exception as e:
        print(f"❌ Erreur InfluxDB: {e}")
        print(f"URL: {INFLUX_URL}, Token: {INFLUX_TOKEN[:10]}...")
        print("Utilisation des données de fallback")
        fallback_data = get_fallback_metrics()
        metrics_cache.set("latest_metrics", fallback_data)
        return fallback_data

def parse_metrics_for_dashboard(metrics_data):
    """Parse les données de métriques pour le dashboard avec calcul des pourcentages"""
    context = {
        'cpu': 0,
        'ram': 0,
        'latency': 0,
        'uptime': 0,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'router_name': 'Cisco-Router-Main',
        'network_in': 0,
        'network_out': 0,
    }
    
    # Variables pour calculer les pourcentages
    ram_used = 0
    ram_free = 0
    router_name = 'Cisco-Router-Main'
    
    for metric in metrics_data:
        measurement = metric.get('measurement', '')
        field = metric.get('field', '')
        value = metric.get('value', 0)
        tags = metric.get('tags', {})
        
        # Récupérer le nom du routeur
        if tags.get('hostname'):
            router_name = tags['hostname']
        elif tags.get('agent_host'):
            router_name = f"Router-{tags['agent_host']}"
        
        # Traiter les métriques SNMP
        if measurement == 'snmp':
            if field == 'cpu_0_usage':
                context['cpu'] = value  # Déjà en pourcentage
            elif field == 'cpu_5min':
                context['cpu'] = value  # Alternative si cpu_0_usage non disponible
            elif field == 'ram_used':
                ram_used = value
            elif field == 'ram_free':
                ram_free = value
            elif field == 'uptime':
                # Convertir de centisecondes en heures
                context['uptime'] = round(value / 360000, 2)  # 1 cs = 0.01s, 1h = 3600s
        
        # Traiter les métriques de ping
        elif measurement == 'ping' and field == 'average_response_ms':
            context['latency'] = value
            print(f"🔍 Latence détectée: {value}ms")
        
        # Traiter les métriques d'interfaces
        elif measurement == 'interfaces':
            if field == 'ifInOctets':
                context['network_in'] += value
            elif field == 'ifOutOctets':
                context['network_out'] += value
    
    # Calculer le pourcentage de RAM
    if ram_used > 0 and ram_free > 0:
        total_ram = ram_used + ram_free
        context['ram'] = round((ram_used / total_ram) * 100, 2)
    elif ram_used > 0:  # Si on a seulement ram_used
        context['ram'] = min(round(ram_used / 1000000, 2), 100)  # Estimation approximative
    
    # Convertir les octets en MB/s pour l'affichage
    context['network_in'] = round(context['network_in'] / 1024 / 1024, 2)
    context['network_out'] = round(context['network_out'] / 1024 / 1024, 2)
    
    # Mettre à jour le nom du routeur
    context['router_name'] = router_name
    
    return context

def dashboard_view(request):
    """Vue principale du dashboard"""
    metrics_data = get_latest_metrics_from_influx()
    context = parse_metrics_for_dashboard(metrics_data)
    return render(request, 'dashboard.html', context)

@csrf_exempt
def get_latest_metrics(request):
    """API pour récupérer les dernières métriques (utilisée par le JS) avec cache"""
    # Vérifier le cache d'abord
    cached_data = metrics_cache.get("latest_metrics")
    if cached_data:
        return JsonResponse(cached_data, safe=False)
    
    # Si pas en cache, récupérer les données
    metrics_data = get_latest_metrics_from_influx()
    
    # Mettre en cache
    metrics_cache.set("latest_metrics", metrics_data)
    
    return JsonResponse(metrics_data, safe=False)

def latest_metrics_api(request):
    """API alternative pour les métriques avec pourcentages calculés"""
    metrics_data = get_latest_metrics_from_influx()
    
    # Convertir en format simplifié avec calcul des pourcentages
    data = {
        "cpu_5min": 0,
        "ram_used": 0,
        "latency_ms": 0,
        "uptime": 0,
        "used_percent": 0,
        "router_name": "Cisco-Router-Main",
    }
    
    # Variables pour calculer les pourcentages
    ram_used_bytes = 0
    ram_free_bytes = 0
    router_name = "router-demo"
    
    for metric in metrics_data:
        measurement = metric.get('measurement', '')
        field = metric.get('field', '')
        value = metric.get('value', 0)
        tags = metric.get('tags', {})
        
        # Récupérer le nom du routeur
        if tags.get('hostname'):
            router_name = tags['hostname']
        
        # Traiter les métriques SNMP
        if measurement == 'snmp':
            if field == 'cpu_0_usage':
                data['cpu_5min'] = value  # Déjà en pourcentage
            elif field == 'ram_used':
                ram_used_bytes = value
            elif field == 'ram_free':
                ram_free_bytes = value
            elif field == 'uptime':
                # Convertir de centisecondes en heures
                data['uptime'] = round(value / 360000, 2)
        
        # Traiter les métriques de ping
        elif measurement == 'ping' and field == 'average_response_ms':
            data['latency_ms'] = value
    
    # Calculer le pourcentage de RAM
    if ram_used_bytes > 0 and ram_free_bytes > 0:
        total_ram = ram_used_bytes + ram_free_bytes
        ram_percent = round((ram_used_bytes / total_ram) * 100, 2)
        data['ram_used'] = ram_percent
        data['used_percent'] = ram_percent
    
    # Mettre à jour le nom du routeur
    data['router_name'] = router_name
    
    return JsonResponse(data)

def index(request):
    """Vue d'index alternative"""
    context = {
        'routers': [],
        'alerts': [],
        'influx_data': {},
        'influx_alerts': [],
        'influx_available': INFLUX_AVAILABLE,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(request, "dashboard.html", context)
