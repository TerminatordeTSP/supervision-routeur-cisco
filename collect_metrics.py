#!/usr/bin/env python3
import subprocess
import time
import json
import os
import re

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
            parsed = parse_telegraf_output(result.stdout)

            with open("metrics_filtered.json", "w") as f:
                json.dump(parsed, f, indent=2)
            print("📦 Données enregistrées dans metrics_filtered.json")

            time.sleep(5)
    finally:
        print("🛑 Collecte arrêtée (run.flag supprimé).")

if __name__ == "__main__":
    main()
