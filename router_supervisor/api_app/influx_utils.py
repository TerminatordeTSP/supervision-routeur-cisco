"""
InfluxDB visualization utilities for the Django dashboard
"""

from my_influxdb_client import InfluxDBClient
from django.conf import settings
import json
import os
from datetime import datetime, timedelta


class InfluxDBDashboard:
    """
    Utility class to get data from InfluxDB for dashboard visualization
    """
    
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token')
        self.org = os.getenv('INFLUXDB_ORG', 'telecom-sudparis')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'router-metrics')
        
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.query_api = self.client.query_api()
    
    def get_router_list(self):
        """Get list of all routers that have sent data"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          |> group(columns: ["router_name"])
          |> distinct(column: "router_name")
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        routers = []
        
        for table in result:
            for record in table.records:
                router_name = record.values.get('router_name')
                if router_name:
                    routers.append(router_name)
        
        return list(set(routers))
    
    def get_router_current_status(self, router_name):
        """Get the most recent metrics for a router"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          |> filter(fn: (r) => r["router_name"] == "{router_name}")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        for table in result:
            for record in table.records:
                return {
                    'router_name': record.values.get('router_name'),
                    'timestamp': record.get_time(),
                    'cpu_usage': record.values.get('cpu_usage', 0),
                    'memory_usage': record.values.get('memory_usage', 0),
                    'traffic_mbps': record.values.get('traffic_mbps', 0)
                }
        
        return None
    
    def get_router_timeseries(self, router_name, hours=24, field='cpu_usage'):
        """Get time series data for a specific router and field"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          |> filter(fn: (r) => r["router_name"] == "{router_name}")
          |> filter(fn: (r) => r["_field"] == "{field}")
          |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    'time': record.get_time().isoformat(),
                    'value': record.values.get('_value', 0)
                })
        
        return data
    
    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        routers = self.get_router_list()
        dashboard_data = {
            'routers': [],
            'total_routers': len(routers),
            'timestamp': datetime.now().isoformat()
        }
        
        for router in routers:
            status = self.get_router_current_status(router)
            if status:
                # Get recent trends
                cpu_trend = self.get_router_timeseries(router, hours=1, field='cpu_usage')
                memory_trend = self.get_router_timeseries(router, hours=1, field='memory_usage')
                
                router_data = {
                    'name': router,
                    'current_status': status,
                    'trends': {
                        'cpu': cpu_trend[-10:] if cpu_trend else [],  # Last 10 points
                        'memory': memory_trend[-10:] if memory_trend else []
                    }
                }
                dashboard_data['routers'].append(router_data)
        
        return dashboard_data
    
    def get_alerts(self, cpu_threshold=80, memory_threshold=85):
        """Get alerts for routers exceeding thresholds"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -5m)
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> filter(fn: (r) => r["cpu_usage"] > {cpu_threshold} or r["memory_usage"] > {memory_threshold})
          |> sort(columns: ["_time"], desc: true)
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        alerts = []
        for table in result:
            for record in table.records:
                cpu = record.values.get('cpu_usage', 0)
                memory = record.values.get('memory_usage', 0)
                
                alert = {
                    'router_name': record.values.get('router_name'),
                    'timestamp': record.get_time(),
                    'severity': 'critical' if cpu > 90 or memory > 95 else 'warning',
                    'message': f"High resource usage - CPU: {cpu:.1f}%, Memory: {memory:.1f}%"
                }
                alerts.append(alert)
        
        return alerts
    
    def close(self):
        """Close the InfluxDB client"""
        self.client.close()


def get_influx_dashboard_context():
    """
    Django view helper function to get InfluxDB data for templates
    """
    try:
        dashboard = InfluxDBDashboard()
        data = dashboard.get_dashboard_data()
        alerts = dashboard.get_alerts()
        dashboard.close()
        
        return {
            'influx_data': data,
            'influx_alerts': alerts,
            'influx_available': True
        }
    except Exception as e:
        return {
            'influx_data': None,
            'influx_alerts': [],
            'influx_available': False,
            'influx_error': str(e)
        }
