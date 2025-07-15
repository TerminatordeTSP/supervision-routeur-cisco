#!/usr/bin/env python3

import sys
sys.path.append('.')

from influxdb_client import InfluxDBClient

# Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

def test_uptime():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    
    # Requête pour récupérer la dernière valeur d'uptime
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "snmp")
      |> filter(fn: (r) => r["_field"] == "uptime")
      |> filter(fn: (r) => r["agent_host"] == "172.16.10.41")
      |> last()
    '''
    
    result = query_api.query(org=INFLUX_ORG, query=query)
    
    for table in result:
        for record in table.records:
            raw_value = record.get_value()
            print(f"Valeur brute d'uptime: {raw_value}")
            print(f"Type: {type(raw_value)}")
            
            # Différentes conversions possibles
            print(f"En secondes (si centisecondes): {raw_value / 100}")
            print(f"En heures (si centisecondes): {raw_value / 360000}")
            print(f"En jours (si centisecondes): {raw_value / 8640000}")
            
            print(f"En heures (si millisecondes): {raw_value / 3600000}")
            print(f"En heures (si secondes): {raw_value / 3600}")
            print(f"En jours (si secondes): {raw_value / 86400}")
    
    client.close()

if __name__ == "__main__":
    test_uptime()
