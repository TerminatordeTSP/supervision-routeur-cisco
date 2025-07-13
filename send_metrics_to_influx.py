import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

def format_value(key, value):
    # Arrondir les pourcentages
    if "percent" in key or "cpu" in key:
        try:
            return round(float(value), 2)
        except Exception:
            return value
    # Convertir octets/s en Mbit/s pour les interfaces
    if key in ("in_bytes", "out_bytes", "in_octets", "out_octets"):
        try:
            return round(float(value) * 8 / 1_000_000, 3)  # Mbit/s
        except Exception:
            return value
    return value

def main():
    with open("metrics_filtered.json", "r") as f:
        metrics = json.load(f)

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

        # Correction du timestamp
        ts = data.get("timestamp")
        timestamp = int(ts) if ts and str(ts).isdigit() else None

        # Préparation du point
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
    print("✅ Toutes les métriques ont été envoyées à InfluxDB (formatées).")

if __name__ == "__main__":
    main()

