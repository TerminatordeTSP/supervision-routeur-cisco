import sys
sys.path.append('/workspace')
from influxdb_client import InfluxDBClient

INFLUX_URL = 'http://influxdb:8086'
INFLUX_TOKEN = 'BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=='
INFLUX_ORG = 'telecom-sudparis'
INFLUX_BUCKET = 'router-metrics'

with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
    query_api = client.query_api()
    
    # Chercher les données d'interfaces
    flux_query = '''
        from(bucket:"router-metrics")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "interfaces" or r._measurement == "snmp")
        |> filter(fn: (r) => r._field =~ /^if.*/)
        |> sort(columns: ["_time"], desc:true)
        |> limit(n:10)
    '''
    
    tables = query_api.query(flux_query)
    interfaces_found = []
    
    for table in tables:
        for record in table.records:
            interface_info = {
                'measurement': record.get_measurement(),
                'field': record.get_field(),
                'value': record.get_value(),
                'time': record.get_time(),
                'tags': dict(record.values)
            }
            
            # Extraire le nom de l'interface
            if 'ifDescr' in interface_info['tags']:
                interface_info['interface_name'] = interface_info['tags']['ifDescr']
            elif 'interface' in interface_info['tags']:
                interface_info['interface_name'] = interface_info['tags']['interface']
            
            interfaces_found.append(interface_info)
    
    if interfaces_found:
        print(f'=== {len(interfaces_found)} données d\'interfaces trouvées ===')
        for i, interface in enumerate(interfaces_found[:5]):  # Limiter à 5 pour l'affichage
            print(f'{i+1}. Interface: {interface.get("interface_name", "N/A")}')
            print(f'   Mesure: {interface["measurement"]}, Champ: {interface["field"]}')
            print(f'   Valeur: {interface["value"]}')
            print(f'   Tags: {interface["tags"]}')
            print()
    else:
        print('Aucune donnée d\'interface trouvée')
