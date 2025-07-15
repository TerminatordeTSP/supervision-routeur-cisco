from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Simple threshold test - ONLY test for CPU threshold violations'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'🧪 SIMPLIFIED THRESHOLD TEST at {timezone.now()}')
        )
        
        try:
            from router_supervisor.api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            from router_supervisor.core_models.models import Router
            
            client = get_influx_client()
            if not client:
                self.stdout.write(self.style.ERROR('❌ Failed to get InfluxDB client'))
                return
            
            router = Router.objects.first()
            self.stdout.write(f'🖥️  Testing router: {router.name}')
            
            threshold = router.threshold
            self.stdout.write(f'🎯 CPU threshold: {threshold.cpu}%')
            
            # Test the CPU query that we know works
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
            
            found_data = False
            for table in result:
                for record in table.records:
                    found_data = True
                    cpu_value = float(record.get_value())
                    timestamp = record.get_time()
                    host = record.values.get('host', 'unknown')
                    
                    threshold_exceeded = cpu_value > float(threshold.cpu)
                    
                    if threshold_exceeded:
                        self.stdout.write(self.style.SUCCESS('🚨 ALERT CONDITION DETECTED!'))
                        self.stdout.write(f'   Router: {host}')
                        self.stdout.write(f'   CPU: {cpu_value}% > {threshold.cpu}% threshold')
                        self.stdout.write(f'   Time: {timestamp}')
                        self.stdout.write(f'   ⚠️  This SHOULD create an alert!')
                        
                        # Log for verification
                        logger.warning(f'THRESHOLD EXCEEDED: {host} CPU = {cpu_value}% > {threshold.cpu}%')
                        
                    else:
                        self.stdout.write(f'✅ CPU OK: {cpu_value}% <= {threshold.cpu}%')
                        self.stdout.write(f'   Router: {host}')
                        self.stdout.write(f'   CPU: {cpu_value}%')
                        self.stdout.write(f'   Time: {timestamp}')
            
            if not found_data:
                self.stdout.write('❌ No CPU data found for configured router')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Test failed: {str(e)}'))
