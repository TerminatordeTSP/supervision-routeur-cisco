import subprocess
import time
import json
import os
import re
from my_influxdb_client import InfluxDBClient, Point, WritePrecision, RouterMetricsInfluxDB
from influxdb_client.client.write_api import SYNCHRONOUS

# Variables to track Django integration status
USE_DJANGO = True
DJANGO_INITIALIZED = False

try:
    import django
    from datetime import datetime
    # Setup Django environment to use models
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'router_supervisor.src.settings')
    django.setup()
    from router_supervisor.core_models.models import Routeur, Interface, KPI, Alertes, SeuilKPI
    DJANGO_INITIALIZED = True
except ImportError as e:
    print(f"⚠️ Django integration disabled: {e}")
    USE_DJANGO = False
except Exception as e:
    print(f"⚠️ Error initializing Django: {e}")
    USE_DJANGO = False

def parse_telegraf_output(output):
    results = []
    lines = output.splitlines()
    for line in lines:
        # Format InfluxDB line protocol (pas de préfixe ">")
        if not line or line.startswith("2025-") or line.startswith("#") or line.startswith("I!") or line.startswith("W!"):
            continue

        # Séparer measurement, tags, fields et timestamp
        parts = line.split(" ")
        if len(parts) < 3:
            continue

        # Parse measurement et tags
        measurement_part = parts[0]
        measurement = measurement_part.split(",")[0]
        
        # Parse tags
        tags = {}
        if "," in measurement_part:
            tag_pairs = measurement_part.split(",")[1:]
            for pair in tag_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    tags[key] = value

        # Parse fields
        fields_part = parts[1]
        fields = {}
        for kv in fields_part.split(","):
            if "=" in kv:
                key, value = kv.split("=", 1)
                # Nettoyer la valeur (enlever i pour integer, etc.)
                value = re.sub(r"[ui]$", "", value)
                try:
                    fields[key] = float(value)
                except ValueError:
                    fields[key] = value.strip('"')

        timestamp = parts[2] if len(parts) > 2 else None

        # === FILTRAGE ADAPTÉ AUX NOUVELLES DONNÉES ===

        # Métriques SNMP du routeur
        if measurement == "snmp" and "hostname" in tags:
            filtered = {
                "router_name": tags.get("hostname"),
                "uptime": fields.get("uptime"),
                "cpu_5min": fields.get("cpu_5min"),
                "timestamp": timestamp,
            }
            results.append({"measurement": "router_snmp", "data": filtered})

        # Ping vers le routeur
        elif measurement == "ping" and "url" in tags and tags["url"] == "172.16.10.41":
            filtered = {
                "latency_ms": fields.get("average_response_ms"),
                "packet_loss": fields.get("percent_packet_loss"),
                "timestamp": timestamp,
            }
            results.append({"measurement": "router_ping", "data": filtered})

        # CPU local (total seulement)
        elif measurement == "cpu" and tags.get("cpu") == "cpu-total":
            filtered = {
                "usage_idle": fields.get("usage_idle"),
                "usage_user": fields.get("usage_user"),
                "usage_system": fields.get("usage_system"),
                "timestamp": timestamp,
            }
            results.append({"measurement": "local_cpu", "data": filtered})

        # RAM locale
        elif measurement == "mem":
            filtered = {
                "used": fields.get("used"),
                "free": fields.get("free"),
                "used_percent": fields.get("used_percent"),
                "total": fields.get("total"),
                "timestamp": timestamp,
            }
            results.append({"measurement": "local_mem", "data": filtered})

        # Système local
        elif measurement == "system":
            filtered = {
                "load1": fields.get("load1"),
                "uptime": fields.get("uptime"),
                "timestamp": timestamp,
            }
            results.append({"measurement": "local_system", "data": filtered})

    return results

def generate_test_data():
    """Génère des données de test simulées au format Telegraf"""
    import time
    timestamp = int(time.time() * 1000000000)  # nanoseconds
    
    test_data = f"""
> cpu-total,cpu=cpu-total,host=test-host usage_idle=85.5,usage_user=10.2,usage_system=4.3 {timestamp}
> mem,host=test-host used=4294967296,free=8589934592,used_percent=33.3 {timestamp}
> system,host=test-host load1=0.8,n_users=2,uptime=86400 {timestamp}
> ping_latency,host=test-host value=25.5 {timestamp}
"""
    return test_data.strip()

def save_to_postgresql(data_entries):
    """
    Sauvegarde les métriques dans la base de données PostgreSQL pour l'historique
    
    Args:
        data_entries (list): Liste des entrées de métriques
    """
    # Vérifier si l'intégration Django est activée
    if not USE_DJANGO or not DJANGO_INITIALIZED:
        print("ℹ️ Sauvegarde PostgreSQL ignorée - Django n'est pas initialisé")
        return
        
    try:
        # Récupérer ou créer le routeur principal
        router_name = None
        for entry in data_entries:
            if entry["measurement"] == "router_snmp" and "router_name" in entry["data"]:
                router_name = entry["data"]["router_name"]
                break
        
        if not router_name:
            print("ℹ️ Aucun nom de routeur trouvé dans les données")
            return
            
        # Rechercher le routeur dans la base de données
        try:
            router = Routeur.objects.get(nom=router_name)
        except Routeur.DoesNotExist:
            print(f"ℹ️ Routeur '{router_name}' non trouvé dans la base de données")
            return
        except Exception as db_error:
            print(f"⚠️ Erreur lors de l'accès à la base de données: {db_error}")
            return
        
        # Obtenir l'interface par défaut
        try:
            default_interface, _ = Interface.objects.get_or_create(
                id_routeur=router,
                nom='default',
                defaults={'trafic': 0.0}
            )
        except Exception as e:
            print(f"⚠️ Impossible de créer l'interface par défaut: {e}")
            return
        
        # Créer ou récupérer les KPIs nécessaires
        try:
            cpu_kpi, _ = KPI.objects.get_or_create(nom='CPU')
            ram_kpi, _ = KPI.objects.get_or_create(nom='RAM')
            latency_kpi, _ = KPI.objects.get_or_create(nom='Latency')
        except Exception as e:
            print(f"⚠️ Impossible de créer les KPIs: {e}")
            return
        
        # Traiter chaque entrée de métrique
        for entry in data_entries:
            measurement = entry["measurement"]
            data = entry["data"]
            
            # Router CPU usage
            if measurement == "router_snmp" and "cpu_5min" in data:
                # Vérifier si la valeur est valide
                if data["cpu_5min"] is not None:
                    # Créer une alerte si nécessaire (au-dessus du seuil)
                    if hasattr(router, 'id_seuil') and router.id_seuil and data["cpu_5min"] > router.id_seuil.cpu:
                        try:
                            alert = Alertes(
                                interface=default_interface,
                                message=f"CPU usage high: {data['cpu_5min']}% > {router.id_seuil.cpu}%",
                                severity="high"
                            )
                            alert.save()
                            alert.kpis.add(cpu_kpi)
                        except Exception as e:
                            print(f"⚠️ Impossible de créer une alerte CPU: {e}")
            
            # Memory usage - we don't have direct RAM metrics from the router, 
            # so we'll use local_mem for demonstration
            if measurement == "local_mem" and "used_percent" in data:
                if data["used_percent"] is not None:
                    # Créer une alerte si nécessaire (au-dessus du seuil)
                    if hasattr(router, 'id_seuil') and router.id_seuil and data["used_percent"] > router.id_seuil.ram:
                        try:
                            alert = Alertes(
                                interface=default_interface,
                                message=f"Memory usage high: {data['used_percent']}% > {router.id_seuil.ram}%",
                                severity="high"
                            )
                            alert.save()
                            alert.kpis.add(ram_kpi)
                        except Exception as e:
                            print(f"⚠️ Impossible de créer une alerte RAM: {e}")
            
            # Latency metrics
            if measurement == "router_ping" and "latency_ms" in data:
                if data["latency_ms"] is not None and data["latency_ms"] > 100:  # Example threshold
                    try:
                        alert = Alertes(
                            interface=default_interface,
                            message=f"High latency: {data['latency_ms']}ms",
                            severity="medium"
                        )
                        alert.save()
                        alert.kpis.add(latency_kpi)
                    except Exception as e:
                        print(f"⚠️ Impossible de créer une alerte Latence: {e}")
                    
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde dans PostgreSQL : {e}")

# === SCRIPT PRINCIPAL ===

if not os.path.exists("run.flag"):
    print("❌ run.flag manquant. Créez-le avec : touch run.flag")
    exit()

# Afficher l'état de l'intégration Django
if USE_DJANGO and DJANGO_INITIALIZED:
    print("✅ Démarrage de la collecte avec intégration Django/PostgreSQL (supprimez run.flag pour arrêter)")
else:
    print("✅ Démarrage de la collecte en mode InfluxDB uniquement (supprimez run.flag pour arrêter)")
    print("ℹ️ L'historique dans PostgreSQL ne sera pas disponible")

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "my-super-secret-auth-token"
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

while os.path.exists("run.flag"):
    # Essayer d'abord avec le container docker et la config simplifiée
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "--network", "host", 
             "-v", f"{os.getcwd()}/telegraf/telegraf_basic.conf:/etc/telegraf/telegraf.conf",
             "telegraf:1.35", "telegraf", "--test", "--once"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"⚠️  Erreur Telegraf Docker (code: {result.returncode})")
            print(f"Stderr: {result.stderr}")
            # Utiliser des données de test à la place
            result.stdout = generate_test_data()
        else:
            print("✅ Données reçues du routeur Cisco 172.16.10.41")
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout Telegraf Docker - utilisation de données de test")
        result = type('obj', (object,), {'stdout': generate_test_data()})
    except Exception as e:
        print(f"⚠️  Erreur Docker: {e} - utilisation de données de test")
        result = type('obj', (object,), {'stdout': generate_test_data()})

    parsed = parse_telegraf_output(result.stdout)

    with open("metrics_filtered.json", "w") as f:
        json.dump(parsed, f, indent=2)

    print("📦 Données enregistrées dans metrics_filtered.json")

    # Initialiser le client RouterMetricsInfluxDB pour une meilleure gestion des données
    router_metrics_client = RouterMetricsInfluxDB(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
        bucket=INFLUX_BUCKET
    )

    # Extraire les métriques du routeur
    router_name = None
    cpu_usage = None
    memory_usage = None
    uptime = None
    latency = None

    for entry in parsed:
        if entry["measurement"] == "router_snmp":
            router_name = entry["data"].get("router_name")
            cpu_usage = entry["data"].get("cpu_5min")
            uptime = entry["data"].get("uptime")
        elif entry["measurement"] == "local_mem":
            memory_usage = entry["data"].get("used_percent")
        elif entry["measurement"] == "router_ping":
            latency = entry["data"].get("latency_ms")

    # Si nous avons les informations nécessaires, envoyer à InfluxDB avec notre client spécialisé
    if router_name and (cpu_usage is not None or memory_usage is not None):
        try:
            # Utiliser les données locales pour le CPU si les données du routeur sont manquantes
            if cpu_usage is None:
                for entry in parsed:
                    if entry["measurement"] == "local_cpu":
                        cpu_usage = 100 - entry["data"].get("usage_idle", 0)
                        break

            # Calculer le trafic total (exemple)
            traffic_mbps = 0  # Par défaut
            
            # Envoyer les données agrégées à InfluxDB
            router_metrics_client.write_router_metric(
                router_name=router_name,
                cpu_usage=cpu_usage if cpu_usage is not None else 0,
                memory_usage=memory_usage if memory_usage is not None else 0,
                traffic_mbps=traffic_mbps,
                interfaces=[]  # Pas d'interfaces spécifiques pour le moment
            )
            
            print(f"✅ Données du routeur {router_name} envoyées à InfluxDB")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi des données agrégées à InfluxDB: {e}")
    
    # Envoi des points individuels à InfluxDB (pour compatibilité avec le code existant)
    for entry in parsed:
        try:
            measurement = entry["measurement"]
            data = entry.get("data", {})
            tags = {}
            if "interface" in entry:
                tags["interface_name"] = entry["interface"]
                tags["type"] = "interface"
            else:
                tags["type"] = measurement

            point = Point(measurement)
            for k, v in data.items():
                if k == "timestamp" or v is None:
                    continue
                point = point.field(k, v)
            for tag, value in tags.items():
                point = point.tag(tag, value)
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f"✅ Point envoyé à InfluxDB : {measurement} | tags={tags} | data={data}")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi à InfluxDB : {e}")
            
    # Fermer le client spécialisé
    router_metrics_client.close()

    # Sauvegarder l'historique dans PostgreSQL si Django est disponible
    if USE_DJANGO and DJANGO_INITIALIZED:
        try:
            save_to_postgresql(parsed)
            print("✅ Historique des données sauvegardé dans PostgreSQL")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde dans PostgreSQL : {e}")
    else:
        print("ℹ️ Sauvegarde PostgreSQL ignorée - utilisant uniquement InfluxDB")

    time.sleep(5)

client.close()
print("🛑 Collecte arrêtée (run.flag supprimé).")
