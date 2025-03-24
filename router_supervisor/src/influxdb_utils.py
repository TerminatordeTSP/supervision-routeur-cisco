from influxdb_client import InfluxDBClient
from django.conf import settings

def get_influxdb_client():
    return InfluxDBClient(
        url=settings.INFLUXDB_SETTINGS['url'],
        token=settings.INFLUXDB_SETTINGS['token'],
        org=settings.INFLUXDB_SETTINGS['org']
    )

def write_data(data):
    client = get_influxdb_client()
    write_api = client.write_api()
    write_api.write(bucket=settings.INFLUXDB_SETTINGS['bucket'], record=data)

def query_data(query):
    client = get_influxdb_client()
    query_api = client.query_api()
    return query_api.query(query)