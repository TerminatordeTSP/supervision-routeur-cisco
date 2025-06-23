# Ce fichier a été renommé pour éviter les conflits avec le package officiel influxdb-client.
# Placez ici vos fonctions utilitaires ou classes personnalisées pour InfluxDB si besoin.



#!/usr/bin/env python3
"""
InfluxDB Client for Router Metrics
This script provides utilities to interact with InfluxDB for router monitoring data.
"""

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
import json

class RouterMetricsInfluxDB:
    def __init__(self, url="http://localhost:8086", token="my-super-secret-auth-token", 
                 org="telecom-sudparis", bucket="router-metrics"):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.bucket = bucket
        self.org = org
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
    
    def write_router_metric(self, router_name, cpu_usage, memory_usage, traffic_mbps, 
                           interfaces=None, timestamp=None):
        """
        Write router metrics to InfluxDB
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Main router metrics point
        point = Point("router_metrics") \
            .tag("router_name", router_name) \
            .field("cpu_usage", cpu_usage) \
            .field("memory_usage", memory_usage) \
            .field("traffic_mbps", traffic_mbps) \
            .time(timestamp, WritePrecision.NS)
        
        points = [point]
        
        # Interface metrics
        if interfaces:
            for interface in interfaces:
                interface_point = Point("interface_metrics") \
                    .tag("router_name", router_name) \
                    .tag("interface_name", interface.get("name", "unknown")) \
                    .field("status", interface.get("status", "unknown")) \
                    .field("bandwidth", interface.get("bandwidth", 0)) \
                    .field("input_rate", interface.get("input_rate", 0)) \
                    .field("output_rate", interface.get("output_rate", 0)) \
                    .field("errors", interface.get("errors", 0)) \
                    .time(timestamp, WritePrecision.NS)
                points.append(interface_point)
        
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)
    
    def query_router_metrics(self, router_name=None, hours=1):
        """
        Query router metrics from the last N hours
        """
        time_filter = f"-{hours}h"
        router_filter = f'|> filter(fn: (r) => r["router_name"] == "{router_name}")' if router_name else ""
        
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {time_filter})
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          {router_filter}
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        metrics = []
        for table in result:
            for record in table.records:
                metrics.append({
                    'time': record.get_time(),
                    'router_name': record.values.get('router_name'),
                    'cpu_usage': record.values.get('cpu_usage'),
                    'memory_usage': record.values.get('memory_usage'),
                    'traffic_mbps': record.values.get('traffic_mbps')
                })
        
        return metrics
    
    def query_interface_metrics(self, router_name=None, interface_name=None, hours=1):
        """
        Query interface metrics from the last N hours
        """
        time_filter = f"-{hours}h"
        router_filter = f'|> filter(fn: (r) => r["router_name"] == "{router_name}")' if router_name else ""
        interface_filter = f'|> filter(fn: (r) => r["interface_name"] == "{interface_name}")' if interface_name else ""
        
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {time_filter})
          |> filter(fn: (r) => r["_measurement"] == "interface_metrics")
          {router_filter}
          {interface_filter}
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        metrics = []
        for table in result:
            for record in table.records:
                metrics.append({
                    'time': record.get_time(),
                    'router_name': record.values.get('router_name'),
                    'interface_name': record.values.get('interface_name'),
                    'status': record.values.get('status'),
                    'bandwidth': record.values.get('bandwidth'),
                    'input_rate': record.values.get('input_rate'),
                    'output_rate': record.values.get('output_rate'),
                    'errors': record.values.get('errors')
                })
        
        return metrics
    
    def get_router_stats(self, router_name, hours=24):
        """
        Get aggregated stats for a router
        """
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          |> filter(fn: (r) => r["router_name"] == "{router_name}")
          |> group(columns: ["_field"])
          |> mean()
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        stats = {}
        for table in result:
            for record in table.records:
                field_name = record.values.get('_field')
                avg_value = record.values.get('_value')
                stats[f"avg_{field_name}"] = avg_value
        
        return stats
    
    def close(self):
        """Close the InfluxDB client"""
        self.client.close()


def main():
    """Example usage of the InfluxDB client"""
    client = RouterMetricsInfluxDB()
    
    try:
        # Example: Write some test data
        print("Writing test data to InfluxDB...")
        client.write_router_metric(
            router_name="router1",
            cpu_usage=45.5,
            memory_usage=78.2,
            traffic_mbps=120.5,
            interfaces=[
                {
                    "name": "GigabitEthernet0/0",
                    "status": "up",
                    "bandwidth": 1000,
                    "input_rate": 450,
                    "output_rate": 380,
                    "errors": 0
                }
            ]
        )
        
        # Example: Query recent metrics
        print("\nQuerying recent router metrics...")
        metrics = client.query_router_metrics(hours=1)
        for metric in metrics[:5]:  # Show first 5 results
            print(f"Router: {metric['router_name']}, Time: {metric['time']}, "
                  f"CPU: {metric['cpu_usage']}%, Memory: {metric['memory_usage']}%")
        
        # Example: Get router stats
        print("\nGetting router statistics...")
        stats = client.get_router_stats("router1", hours=1)
        for stat_name, value in stats.items():
            print(f"{stat_name}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()