# InfluxDB Integration

This project now includes InfluxDB for time-series data storage and analysis of router metrics.

## Quick Start

1. **Start InfluxDB container:**
   ```bash
   docker-compose up -d influxdb
   ```

2. **Run the setup script:**
   ```bash
   ./setup_influxdb.sh
   ```

3. **Access InfluxDB UI:**
   - URL: http://localhost:8086
   - Username: `admin`
   - Password: `admin123456`

## Configuration

### InfluxDB Settings
- **Organization:** `telecom-sudparis`
- **Bucket:** `router-metrics`
- **Token:** `my-super-secret-auth-token`
- **Port:** `8086`

### Telegraf Integration
Telegraf is configured to send data to both:
- Django API (existing): `http://router_django:8080/api/metrics/`
- InfluxDB (new): `http://influxdb:8086`

## Usage

### 1. Python Client
Use the `influxdb_client.py` script to interact with InfluxDB programmatically:

```python
from influxdb_client import RouterMetricsInfluxDB

client = RouterMetricsInfluxDB()

# Write metrics
client.write_router_metric(
    router_name="router1",
    cpu_usage=45.5,
    memory_usage=78.2,
    traffic_mbps=120.5
)

# Query metrics
metrics = client.query_router_metrics(router_name="router1", hours=1)
print(metrics)

client.close()
```

### 2. Django Management Commands
Query data directly from Django:

```bash
# Show recent metrics
python router_supervisor/manage.py query_influxdb --hours 1

# Show metrics for specific router
python router_supervisor/manage.py query_influxdb --router router1 --hours 24

# Show aggregated statistics
python router_supervisor/manage.py query_influxdb --stats --hours 24
```

### 3. InfluxDB CLI Queries
Connect to InfluxDB and run Flux queries:

```bash
# Enter the InfluxDB container
docker exec -it influxdb influx

# Example query
from(bucket: "router-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "router_metrics")
  |> mean()
```

## Data Schema

### Router Metrics
- **Measurement:** `router_metrics`
- **Tags:** `router_name`
- **Fields:** `cpu_usage`, `memory_usage`, `traffic_mbps`

### Interface Metrics
- **Measurement:** `interface_metrics`
- **Tags:** `router_name`, `interface_name`
- **Fields:** `status`, `bandwidth`, `input_rate`, `output_rate`, `errors`

## Environment Variables

You can customize InfluxDB settings using environment variables:

```bash
export INFLUXDB_URL="http://localhost:8086"
export INFLUXDB_TOKEN="my-super-secret-auth-token"
export INFLUXDB_ORG="telecom-sudparis"
export INFLUXDB_BUCKET="router-metrics"
```

## Troubleshooting

### Check InfluxDB Status
```bash
curl http://localhost:8086/health
```

### View InfluxDB Logs
```bash
docker logs influxdb
```

### Verify Telegraf is Sending Data
```bash
docker logs telegraf
```

### Reset InfluxDB Data
```bash
docker-compose down
docker volume rm supervision-routeur-cisco_influxdb_data
docker volume rm supervision-routeur-cisco_influxdb_config
docker-compose up -d influxdb
```
