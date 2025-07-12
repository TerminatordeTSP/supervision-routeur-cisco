#!/usr/bin/env python3
import subprocess
import time
import json
import os
import re
from influxdb_client import Point, WritePrecision, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


INFLUX_URL = "http://localhost:8086"
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
                "cpu_5min": fields.get("cpu_5min"),
                "cpu_0_usage": fields.get("cpu_0_usage"),
                "cpu_0_index": fields.get("cpu_0_index"),
                "ram_used": fields.get("ram_used"),
                "ram_free": fields.get("ram_free"),
                "timestamp": timestamp,
            }
            if any(v is not None for v in filtered.values()):
                results.append({"measurement": "snmp", "data": filtered})

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

        elif measurement == "ping_latency":
            results.append({
                "measurement": "ping_latency",
                "data": {
                    "latency_ms": fields.get("value"),
                    "timestamp": timestamp,
                }
            })

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

        elif measurement == "system":
            filtered = {
                "n_users": fields.get("n_users"),
                "load1": fields.get("load1"),
                "uptime": fields.get("uptime"),
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

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    client.close()

def main():
    if not os.path.exists("run.flag"):
        print("❌ run.flag manquant. Créez-le avec : touch run.flag")
        return

    try:
        while os.path.exists("run.flag"):
            result = subprocess.run(
                ["telegraf", "--config", "telegraf/telegraf.conf", "--test"],
                capture_output=True,
                text=True,
                env={**os.environ, "MIBS": ""}
            )
            parsed_metrics = parse_telegraf_output(result.stdout)
            send_to_influx(parsed_metrics)
            print("✅ Données envoyées à InfluxDB.")
            time.sleep(5)
    finally:
        print("🛑 Pipeline arrêté (run.flag supprimé).")

if __name__ == "__main__":
    main()
