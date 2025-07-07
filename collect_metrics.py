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
        if not line.startswith(">"):
            continue

        line = line[2:]  # Enlève "> "
        parts = line.split(" ")
        if len(parts) < 3:
            continue

        measurement = parts[0].split(",")[0]
        tags = dict(item.split("=") for item in parts[0].split(",")[1:] if "=" in item)
        fields_raw = parts[1].split(",")
        fields = {}

        for kv in fields_raw:
            if "=" in kv:
                key, value = kv.split("=")
                value = re.sub(r"[ui]$", "", value)  # Enlève le u ou i final
                try:
                    fields[key] = float(value)
                except ValueError:
                    fields[key] = value

        timestamp = parts[2]

        # === FILTRAGE ===

        # Métriques générales SNMP
        if measurement == "snmp":
            filtered = {
                "cpu_5min": fields.get("cpu_5min"),
                "cpu_0_usage": fields.get("cpu_0_usage"),
                "cpu_0_index": fields.get("cpu_0_index"),
                "ram_used": fields.get("ram_used"),
                "ram_free": fields.get("ram_free"),
                "timestamp": timestamp,
            }
            if any(v is not None for v in filtered.values()):
                results.append({"measurement": "snmp", "data": filtered})

        # Interfaces – on garde toutes celles détectées
        elif measurement == "interfaces" and "ifDescr" in tags:
            filtered = {
                "ifInOctets": fields.get("ifInOctets"),
                "ifOutOctets": fields.get("ifOutOctets"),
                "ifInErrors": fields.get("ifInErrors"),
                "ifOutErrors": fields.get("ifOutErrors"),
                "timestamp": timestamp,
            }
            results.append({
                "measurement": "interfaces",
                "interface": tags["ifDescr"],
                "data": filtered
            })

        # Ping
        elif measurement == "ping_latency":
            results.append({
                "measurement": "ping_latency",
                "data": {
                    "latency_ms": fields.get("value"),
                    "timestamp": timestamp,
                }
            })

        # CPU machine hôte (résumé total uniquement)
        elif measurement == "cpu-total":
            results.append({
                "measurement": "cpu-total",
                "data": {
                    "usage_idle": fields.get("usage_idle"),
                    "usage_user": fields.get("usage_user"),
                    "usage_system": fields.get("usage_system"),
                    "timestamp": timestamp,
                }
            })

        # RAM machine hôte
        elif measurement == "mem":
            results.append({
                "measurement": "mem",
                "data": {
                    "used": fields.get("used"),
                    "free": fields.get("free"),
                    "used_percent": fields.get("used_percent"),
                    "timestamp": timestamp,
                }
            })

        # Système machine hôte (filtrage utile)
        elif measurement == "system":
            filtered = {
                "n_users": fields.get("n_users"),
                "load1": fields.get("load1"),
                "uptime": fields.get("uptime"),
                "timestamp": timestamp,
            }
            # On n’ajoute que si on a au moins un champ pertinent
            if any(v is not None for v in [filtered["n_users"], filtered["load1"], filtered["uptime"]]):
                results.append({
                    "measurement": "system",
                    "data": filtered
                })

    return results

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
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

while os.path.exists("run.flag"):
    result = subprocess.run(
        ["telegraf", "--config", "telegraf/telegraf.conf", "--test"],
        capture_output=True,
        text=True
    )

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
