import os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "TSP"
url = "http://172.16.10.40:8086"
bucket = "cisco-supervisor"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
   
"""for value in range(5):
  point = (
    Point("measurement1")
    .tag("tagname1", "tagvalue1")
    .field("field1", value)
  )
  write_api.write(bucket=bucket, org="TSP", record=point)
  time.sleep(1) # separate points by 1 second
"""

"""for value in range(5):
    point = (
        Point("measurement1")
        .tag("tagname1", "tagvalue1")
        .field("field1", value)
    ) 
    write_api.write(bucket=bucket, org="TSP", record=point)
    time.sleep(1) # separate points by 1 second

print("Data written successfully.")"""



query_api = client.query_api()

query = """from(bucket: "cisco-supervisor")
 |> range(start: -10m)
 |> filter(fn: (r) => r._measurement == "measurement1")"""
tables = query_api.query(query, org="TSP")

for table in tables:
  for record in table.records:
    print(f'{record}\n')