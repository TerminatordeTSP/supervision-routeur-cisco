from django.core.management.base import BaseCommand
from influxdb_client import InfluxDBClient
import os


class Command(BaseCommand):
    help = 'Query router metrics from InfluxDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--router',
            type=str,
            help='Router name to query (optional)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Number of hours to look back (default: 1)',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show aggregated statistics',
        )

    def handle(self, *args, **options):
        # InfluxDB connection settings
        url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        token = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token')
        org = os.getenv('INFLUXDB_ORG', 'telecom-sudparis')
        bucket = os.getenv('INFLUXDB_BUCKET', 'router-metrics')

        client = InfluxDBClient(url=url, token=token, org=org)
        query_api = client.query_api()

        try:
            if options['stats']:
                self.show_stats(query_api, bucket, org, options['router'], options['hours'])
            else:
                self.show_metrics(query_api, bucket, org, options['router'], options['hours'])
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error querying InfluxDB: {e}')
            )
        finally:
            client.close()

    def show_metrics(self, query_api, bucket, org, router_name, hours):
        """Show recent router metrics"""
        time_filter = f"-{hours}h"
        router_filter = f'|> filter(fn: (r) => r["router_name"] == "{router_name}")' if router_name else ""

        query = f'''
        from(bucket: "{bucket}")
          |> range(start: {time_filter})
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          {router_filter}
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 10)
        '''

        result = query_api.query(org=org, query=query)

        self.stdout.write(
            self.style.SUCCESS(f'Recent router metrics (last {hours} hours):')
        )
        self.stdout.write('-' * 80)

        for table in result:
            for record in table.records:
                time = record.get_time().strftime('%Y-%m-%d %H:%M:%S')
                router = record.values.get('router_name', 'unknown')
                cpu = record.values.get('cpu_usage', 0)
                memory = record.values.get('memory_usage', 0)
                traffic = record.values.get('traffic_mbps', 0)

                self.stdout.write(
                    f"{time} | Router: {router:10} | "
                    f"CPU: {cpu:5.1f}% | Memory: {memory:5.1f}% | "
                    f"Traffic: {traffic:6.1f} Mbps"
                )

    def show_stats(self, query_api, bucket, org, router_name, hours):
        """Show aggregated statistics"""
        time_filter = f"-{hours}h"
        router_filter = f'|> filter(fn: (r) => r["router_name"] == "{router_name}")' if router_name else ""

        query = f'''
        from(bucket: "{bucket}")
          |> range(start: {time_filter})
          |> filter(fn: (r) => r["_measurement"] == "router_metrics")
          {router_filter}
          |> group(columns: ["router_name", "_field"])
          |> mean()
        '''

        result = query_api.query(org=org, query=query)

        self.stdout.write(
            self.style.SUCCESS(f'Router statistics (last {hours} hours):')
        )
        self.stdout.write('-' * 60)

        stats = {}
        for table in result:
            for record in table.records:
                router = record.values.get('router_name', 'unknown')
                field = record.values.get('_field')
                value = record.values.get('_value', 0)
                
                if router not in stats:
                    stats[router] = {}
                stats[router][field] = value

        for router, router_stats in stats.items():
            self.stdout.write(f"\nRouter: {router}")
            for field, value in router_stats.items():
                unit = "%" if field in ['cpu_usage', 'memory_usage'] else "Mbps" if field == 'traffic_mbps' else ""
                self.stdout.write(f"  Average {field}: {value:.2f} {unit}")
