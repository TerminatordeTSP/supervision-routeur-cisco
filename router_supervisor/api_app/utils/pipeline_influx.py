from influxdb_client import InfluxDBClient

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

def query_latest_metrics(measurement, field=None, limit=10, interface=None):
    query_api = None
    results = []
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'from(bucket:"{INFLUX_BUCKET}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "{measurement}")'
        if field:
            flux += f' |> filter(fn: (r) => r._field == "{field}")'
        if interface:
            flux += f' |> filter(fn: (r) => r.interface_name == "{interface}")'
        flux += f' |> sort(columns: ["_time"], desc:true) |> limit(n:{limit})'
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                result = {
                    "time": record.get_time(),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "tags": record.values
                }
                results.append(result)
    return results