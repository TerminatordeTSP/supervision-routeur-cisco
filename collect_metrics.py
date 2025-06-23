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

print("✅ Démarrage de la collecte... (supprimez run.flag pour arrêter)")

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
