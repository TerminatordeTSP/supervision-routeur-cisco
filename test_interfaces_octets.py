import sys
sys.path.append('/workspace')
from influxdb_client import InfluxDBClient

INFLUX_URL = 'http://influxdb:8086'
INFLUX_TOKEN = 'BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=='
INFLUX_ORG = 'telecom-sudparis'
INFLUX_BUCKET = 'router-metrics'

with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
    query_api = client.query_api()
    
    # Chercher les données d'interfaces avec ifInOctets et ifOutOctets
    flux_query = '''
        from(bucket:"router-metrics")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "interfaces")
        |> filter(fn: (r) => r._field == "ifInOctets" or r._field == "ifOutOctets")
        |> sort(columns: ["_time"], desc:true)
        |> group(columns: ["ifDescr", "_field"])
        |> first()
    '''
    
    tables = query_api.query(flux_query)
    interfaces_data = {}
    
    for table in tables:
        for record in table.records:
            interface_name = record.values.get('ifDescr', 'Unknown')
            field = record.get_field()
            value = record.get_value()
            
            if interface_name not in interfaces_data:
                interfaces_data[interface_name] = {}
            
            interfaces_data[interface_name][field] = value
    
    if interfaces_data:
        print(f'=== {len(interfaces_data)} interfaces actives trouvées ===')
        for interface_name, data in interfaces_data.items():
            print(f'Interface: {interface_name}')
            in_octets = data.get('ifInOctets', 0)
            out_octets = data.get('ifOutOctets', 0)
            
            # Convertir en MB
            in_mb = in_octets / (1024 * 1024) if in_octets > 0 else 0
            out_mb = out_octets / (1024 * 1024) if out_octets > 0 else 0
            
            print(f'  - ifInOctets: {in_octets} octets ({in_mb:.2f} MB)')
            print(f'  - ifOutOctets: {out_octets} octets ({out_mb:.2f} MB)')
            print()
    else:
        print('Aucune donnée d\'interface avec ifInOctets/ifOutOctets trouvée')
