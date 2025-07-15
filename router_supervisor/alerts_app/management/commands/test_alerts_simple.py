from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Simple test to verify threshold detection works'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'🧪 Testing threshold detection at {timezone.now()}')
        )
        
        try:
            from router_supervisor.api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            from router_supervisor.core_models.models import Router
            
            client = get_influx_client()
            if not client:
                self.stdout.write(self.style.ERROR('❌ Failed to get InfluxDB client'))
                return
            
            # Get the configured router
            router = Router.objects.first()
            if not router:
                self.stdout.write(self.style.ERROR('❌ No router configured'))
                return
                
            self.stdout.write(f'🖥️  Testing router: {router.name}')
            threshold = router.threshold
            self.stdout.write(f'🎯 CPU threshold: {threshold.cpu}%')
            
            # Test CPU query that we know works
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -2h)
            |> filter(fn: (r) => r._measurement == "snmp")
            |> filter(fn: (r) => r._field == "cpu_0_usage")
            |> filter(fn: (r) => r["host"] == "{router.name}")
            |> sort(columns: ["_time"], desc: true)
            |> limit(n: 1)
            '''
            
            self.stdout.write('\n🔍 Executing CPU query...')
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
                        self.stdout.write(
                            self.style.SUCCESS(f'🔴 THRESHOLD EXCEEDED!')
                        )
                        self.stdout.write(f'   Router: {host}')
                        self.stdout.write(f'   CPU Usage: {cpu_value}%')
                        self.stdout.write(f'   Threshold: {threshold.cpu}%')
                        self.stdout.write(f'   Time: {timestamp}')
                        self.stdout.write(f'   ⚠️  This SHOULD trigger an alert!')
                        
                        # Log the alert
                        logger.warning(f'CPU threshold exceeded: {host} = {cpu_value}% > {threshold.cpu}%')
                        
                    else:
                        self.stdout.write(f'✅ CPU OK: {cpu_value}% <= {threshold.cpu}%')
            
            if not found_data:
                self.stdout.write(self.style.ERROR('❌ No CPU data found'))
                
                # Debug what's available
                debug_query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                |> range(start: -2h)
                |> filter(fn: (r) => r["host"] == "{router.name}")
                |> limit(n: 5)
                '''
                
                debug_result = client.query_api().query(debug_query, org=INFLUXDB_ORG)
                self.stdout.write(f'\n🔍 Available data for {router.name}:')
                
                count = 0
                for table in debug_result:
                    for record in table.records:
                        measurement = record.get_measurement()
                        field = record.get_field()
                        value = record.get_value()
                        time = record.get_time()
                        self.stdout.write(f'   {measurement}.{field} = {value} at {time}')
                        count += 1
                
                if count == 0:
                    self.stdout.write(f'   No data found for {router.name} in last 2 hours')
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Test completed')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during test: {str(e)}')
            )
            logger.error(f'Error in test: {str(e)}', exc_info=True)
