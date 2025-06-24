import subprocess
import time
import json
import os
import re
from my_influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

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

# === SCRIPT PRINCIPAL ===

if not os.path.exists("run.flag"):
    print("❌ run.flag manquant. Créez-le avec : touch run.flag")
    exit()

print("✅ Démarrage de la collecte... (supprimez run.flag pour arrêter)")

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

    # Envoi en temps réel à InfluxDB
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

    time.sleep(5)

client.close()
print("🛑 Collecte arrêtée (run.flag supprimé).")
