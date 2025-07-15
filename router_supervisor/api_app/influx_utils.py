import os
from influxdb_client import InfluxDBClient

# Constants for InfluxDB configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA==')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'telecom-sudparis')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'router-metrics')

def get_influx_client():
    """Get an InfluxDB client instance"""
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        # Test the connection
        client.ping()
        return client
    except Exception as e:
        print(f"Failed to connect to InfluxDB: {e}")
        return None

class InfluxDBDashboard:
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', 'BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA==')
        self.org = os.getenv('INFLUXDB_ORG', 'telecom-sudparis')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'router-metrics')
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.query_api = self.client.query_api()

    def get_interfaces_mbps(self):
        query = f'''
        import "influxdata/influxdb/schema"
        from(bucket: "{self.bucket}")
          |> range(start: -2m)
          |> filter(fn: (r) => r._measurement == "interfaces")
          |> filter(fn: (r) => r._field == "ifInOctets" or r._field == "ifOutOctets")
          |> group(columns: ["interface_name", "_field"])
          |> sort(columns: ["_time"])
          |> tail(n:2)
        '''
        result = self.query_api.query(org=self.org, query=query)
        # Dictionnaire {iface: {"in": Mbps, "out": Mbps}}
        stats = {}
        for table in result:
            iface = None
            field = None
            if len(table.records) < 2:
                continue
            t0, v0 = table.records[0].get_time(), table.records[0].get_value()
            t1, v1 = table.records[1].get_time(), table.records[1].get_value()
            iface = table.records[0].values.get("interface_name")
            field = table.records[0].values.get("_field")
            delta_octets = v1 - v0
            delta_sec = (t1 - t0).total_seconds()
            mbps = (delta_octets * 8 / 1_000_000) / delta_sec if delta_sec > 0 else 0
            if iface not in stats:
                stats[iface] = {}
            if field == "ifInOctets":
                stats[iface]["in"] = mbps
            elif field == "ifOutOctets":
                stats[iface]["out"] = mbps
        return stats

    def close(self):
        self.client.close()

def get_influx_dashboard_context():
    # Get the latest data from InfluxDB for the dashboard
    influx = InfluxDBDashboard()
    interfaces_stats = influx.get_interfaces_mbps()
    influx.close()
    
    return {
        "interfaces": interfaces_stats
    }