import os
from influxdb_client import InfluxDBClient

class InfluxDBDashboard:
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token')
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