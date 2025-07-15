from influxdb_client import InfluxDBClient

INFLUX_URL = 'http://influxdb:8086'
INFLUX_TOKEN = 'BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=='
INFLUX_ORG = 'telecom-sudparis'
INFLUX_BUCKET = 'router-metrics'

with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
    query_api = client.query_api()
    flux_query = f'''
        from(bucket:"{INFLUX_BUCKET}")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "snmp")
        |> filter(fn: (r) => r._field == "uptime")
        |> sort(columns: ["_time"], desc:true)
        |> limit(n:1)
    '''
    tables = query_api.query(flux_query)
    for table in tables:
        for record in table.records:
            print(f'Uptime trouvé: {record.get_value()} (Type: {type(record.get_value())})')
            print(f'Mesure: {record.get_measurement()}, Champ: {record.get_field()}')
            print(f'Temps: {record.get_time()}')
