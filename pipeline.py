#!/usr/bin/env python3
import subprocess
import time
import json
import os
import re
import signal
import sys
from influxdb_client import Point, WritePrecision, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

def parse_telegraf_output(output):
    results = []
    lines = output.splitlines()
    for line in lines:
        if not line.startswith(">"):
            continue
        line = line[2:]
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
                value = re.sub(r"[ui]$", "", value)
                try:
                    fields[key] = float(value)
                except ValueError:
                    fields[key] = value
        timestamp = parts[2]

        if measurement == "snmp":
            filtered = {
                "cpu_5min": float(fields.get("cpu_5min")) if fields.get("cpu_5min") is not None else None,
                "cpu_0_usage": float(fields.get("cpu_0_usage")) if fields.get("cpu_0_usage") is not None else None,
                "cpu_0_index": float(fields.get("cpu_0_index")) if fields.get("cpu_0_index") is not None else None,
                "ram_used": float(fields.get("ram_used")) if fields.get("ram_used") is not None else None,
                "ram_free": float(fields.get("ram_free")) if fields.get("ram_free") is not None else None,
                "timestamp": timestamp,
            }
            if any(v is not None for v in filtered.values()):
                results.append({"measurement": "snmp", "data": filtered})

        elif measurement == "interfaces" and "ifDescr" in tags:
            filtered = {
                "ifInOctets": float(fields.get("ifInOctets")) if fields.get("ifInOctets") is not None else None,
                "ifOutOctets": float(fields.get("ifOutOctets")) if fields.get("ifOutOctets") is not None else None,
                "ifInErrors": float(fields.get("ifInErrors")) if fields.get("ifInErrors") is not None else None,
                "ifOutErrors": float(fields.get("ifOutErrors")) if fields.get("ifOutErrors") is not None else None,
                "timestamp": timestamp,
            }
            results.append({
                "measurement": "interfaces",
                "interface": tags["ifDescr"],
                "data": filtered
            })

        elif measurement == "ping_latency":
            results.append({
                "measurement": "ping_latency",
                "data": {
                    "latency_ms": float(fields.get("value")) if fields.get("value") is not None else None,
                    "timestamp": timestamp,
                }
            })

        elif measurement == "cpu-total":
            results.append({
                "measurement": "cpu-total",
                "data": {
                    "usage_percent": float(fields.get("usage_percent")) if fields.get("usage_percent") is not None else None,
                    "usage_idle": float(fields.get("usage_idle")) if fields.get("usage_idle") is not None else None,
                    "usage_user": float(fields.get("usage_user")) if fields.get("usage_user") is not None else None,
                    "usage_system": float(fields.get("usage_system")) if fields.get("usage_system") is not None else None,
                    "timestamp": timestamp,
                }
            })

        elif measurement == "mem":
            results.append({
                "measurement": "mem",
                "data": {
                    "used": float(fields.get("used")) if fields.get("used") is not None else None,
                    "free": float(fields.get("free")) if fields.get("free") is not None else None,
                    "used_percent": float(fields.get("used_percent")) if fields.get("used_percent") is not None else None,
                    "timestamp": timestamp,
                }
            })

        elif measurement == "system":
            filtered = {
                "n_users": float(fields.get("n_users")) if fields.get("n_users") is not None else None,
                "load1": float(fields.get("load1")) if fields.get("load1") is not None else None,
                "uptime": float(fields.get("uptime")) if fields.get("uptime") is not None else None,
                "timestamp": timestamp,
            }
            if any(v is not None for v in [filtered["n_users"], filtered["load1"], filtered["uptime"]]):
                results.append({
                    "measurement": "system",
                    "data": filtered
                })

    return results

def format_value(key, value):
    if "percent" in key or "cpu" in key:
        try:
            return round(float(value), 2)
        except Exception:
            return value
    if key in ("in_bytes", "out_bytes", "in_octets", "out_octets"):
        try:
            return round(float(value) * 8 / 1_000_000, 3)  # Convertir en Mbit/s
        except Exception:
            return value
    return value

def send_to_influx(metrics):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for entry in metrics:
        measurement = entry["measurement"]
        data = entry.get("data", {})
        tags = {}

        if "interface" in entry:
            tags["interface_name"] = entry["interface"]
            tags["type"] = "interface"
        else:
            tags["type"] = measurement

        ts = data.get("timestamp")
        timestamp = int(ts) if ts and str(ts).isdigit() else None

        point = Point(measurement)
        for k, v in data.items():
            if k == "timestamp" or v is None:
                continue
            point = point.field(k, format_value(k, v))
        for tag, value in tags.items():
            point = point.tag(tag, value)
        if timestamp:
            point = point.time(timestamp, WritePrecision.NS)

        # 🟡 Ajout ICI du print debug :
        print("➡️ Sending to InfluxDB:", point.to_line_protocol())

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    client.close()


def signal_handler(signum, frame):
    """Handle graceful shutdown"""
    print(f"\n🛑 Received signal {signum}. Stopping pipeline...")
    if os.path.exists("run.flag"):
        os.remove("run.flag")
    sys.exit(0)


def main():
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    if not os.path.exists("run.flag"):
        print("❌ run.flag manquant. Créez-le avec : touch run.flag")
        return

    try:
        while os.path.exists("run.flag"):
            result = subprocess.run(
                ["telegraf", "--config", "/etc/telegraf/telegraf.conf", "--test"],
                capture_output=True,
                text=True,
                env={**os.environ, "MIBS": ""}
            )
            parsed_metrics = parse_telegraf_output(result.stdout)
            send_to_influx(parsed_metrics)

            with open("latest_metrics.json", "w") as f:
                json.dump(parsed_metrics, f, indent=2)

            print("✅ Données envoyées à InfluxDB.")
            time.sleep(5)
    finally:
        print("🛑 Pipeline arrêté (run.flag supprimé).")

if __name__ == "__main__":
    main()
