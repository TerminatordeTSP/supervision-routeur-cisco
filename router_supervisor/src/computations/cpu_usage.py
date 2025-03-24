from puresnmp import Client, V3, PyWrapper
from puresnmp.credentials import Auth, Priv
from influxdb_client import InfluxDBClient, Point, WritePrecision
import os
import asyncio
import time

INFLUX_URL = "http://172.16.10.40:8086"
INFLUX_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUX_ORG = "TSP"
INFLUX_BUCKET = "network_metrics"

SNMP_AUTH_TOKEN = os.environ.get("SNMP_AUTH_TOKEN")
SNMP_PRIVACY_TOKEN = os.environ.get("SNMP_PRIVACY_TOKEN")

auth = Auth(SNMP_AUTH_TOKEN.encode('utf-8'), 'md5')
priv = Priv(SNMP_PRIVACY_TOKEN.encode('utf-8'), 'aes')

ROUTER_IP = "172.16.10.41"
COMMUNITY_STRING = "public"
CPU_OID = "1.3.6.1.4.1.9.9.109.1.1.1.1.5" # cpmCPUTotal 1 minute (get from snmp)

async def get_snmp_data(oid):
    try:
        auth = Auth(SNMP_AUTH_TOKEN.encode('utf-8'), 'md5')
        priv = Priv(SNMP_PRIVACY_TOKEN.encode('utf-8'), 'aes')
        client = PyWrapper(Client(ROUTER_IP, V3('SNMPUSER', auth, priv)))
        client.timeout = 10
        result = await client.get(oid)
        return int(result)
    except Exception as e:
        print("SNMP Error:", e)
        return None

def store_in_influx(cpu_usage):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=WritePrecision.NS)

    point = Point("cpu_usage").field("value", cpu_usage)
    write_api.write(bucket=INFLUX_BUCKET, record=point)
    client.close()

async def main():
    start_time = time.time()
    while time.time() - start_time < 60:  # run during 60 seconds for testing purposes
        cpu_usage = await get_snmp_data(CPU_OID)
        if cpu_usage is not None:
            store_in_influx(cpu_usage)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
