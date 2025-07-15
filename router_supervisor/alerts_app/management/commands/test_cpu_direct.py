from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test CPU threshold - Direct approach'

    def handle(self, *args, **options):
        self.stdout.write('🔥 DIRECT CPU TEST STARTING')
        
        try:
            from router_supervisor.api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            from router_supervisor.core_models.models import Router
            
            client = get_influx_client()
            router = Router.objects.first()
            threshold = router.threshold
            
            self.stdout.write(f'Testing {router.name} CPU vs {threshold.cpu}% threshold')
            
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -2h)
            |> filter(fn: (r) => r._measurement == "snmp")
            |> filter(fn: (r) => r._field == "cpu_0_usage")
            |> filter(fn: (r) => r["host"] == "{router.name}")
            |> sort(columns: ["_time"], desc: true)
            |> limit(n: 1)
            '''
            
            result = client.query_api().query(query, org=INFLUXDB_ORG)
            
            for table in result:
                for record in table.records:
                    cpu_value = float(record.get_value())
                    timestamp = record.get_time()
                    host = record.values.get('host', 'unknown')
                    
                    if cpu_value > float(threshold.cpu):
                        self.stdout.write(f'🚨 ALERT: {host} CPU {cpu_value}% > {threshold.cpu}% at {timestamp}')
                    else:
                        self.stdout.write(f'✅ OK: {host} CPU {cpu_value}% <= {threshold.cpu}% at {timestamp}')
                    return
            
            self.stdout.write('❌ No CPU data found')
            
        except Exception as e:
            self.stdout.write(f'ERROR: {str(e)}')
