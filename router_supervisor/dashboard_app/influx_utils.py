from influxdb_client import InfluxDBClient

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

def get_latest_octets():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "snmp")
            |> filter(fn: (r) => r._field == "octets_in")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
    return 0

def get_latest_cpu_usage():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "snmp")
            |> filter(fn: (r) => r._field == "cpu_0_usage")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
    return 0

def get_latest_ram_usage():
    total_ram = 2 * 1024 * 1024 * 1024  # 2 Go en octets
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "snmp")
            |> filter(fn: (r) => r._field == "ram_used")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                ram_used = float(record.get_value())
                ram_percent = (ram_used / total_ram) * 100
                return round(ram_percent, 2)
    return 0

def get_latest_latency():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "ping_latency")
            |> filter(fn: (r) => r._field == "value")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
    return 0

def get_latest_system_load():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "system")
            |> filter(fn: (r) => r._field == "load1")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
    return 0

def get_latest_system_cpu():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "cpu-total")
            |> filter(fn: (r) => r._field == "usage_user")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
    return 0

def get_latest_uptime():
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        query_api = client.query_api()
        flux = f'''
            from(bucket:"{INFLUX_BUCKET}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == "system")
            |> filter(fn: (r) => r._field == "uptime")
            |> sort(columns: ["_time"], desc:true)
            |> limit(n:1)
        '''
        tables = query_api.query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
    return 0

def get_router_name():
    # Met un vrai nom si tu le connais, ou trouve le via une autre query ou setting
    return "Cisco-Router"