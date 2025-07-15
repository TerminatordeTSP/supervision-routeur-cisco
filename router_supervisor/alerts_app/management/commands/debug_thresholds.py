from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug threshold checking - show what data is available and if thresholds are exceeded'

    def add_arguments(self, parser):
        parser.add_argument(
            '--router',
            type=str,
            help='Specific router to check (optional)',
        )

    def handle(self, *args, **options):
        router_filter = options.get('router')
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Starting threshold debug at {timezone.now()}')
        )
        
        try:
            self.check_database_configuration()
            self.check_influxdb_connection()
            self.check_thresholds_and_routers(router_filter)
            self.check_recent_metrics(router_filter)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Debug check completed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during debug: {str(e)}')
            )
            logger.error(f'Error in debug_thresholds command: {str(e)}', exc_info=True)

    def check_database_configuration(self):
        """Check Django database and models"""
        self.stdout.write(self.style.WARNING('\n=== 🗄️  DATABASE CONFIGURATION ==='))
        
        try:
            from router_supervisor.core_models.models import Threshold, Router
            
            thresholds = Threshold.objects.all()
            routers = Router.objects.all()
            
            self.stdout.write(f'📊 Found {thresholds.count()} configured thresholds')
            self.stdout.write(f'🖥️  Found {routers.count()} configured routers')
            
            if thresholds.count() == 0:
                self.stdout.write(self.style.ERROR('❌ No thresholds configured! You need to create thresholds in the admin interface.'))
            
            if routers.count() == 0:
                self.stdout.write(self.style.ERROR('❌ No routers configured! You need to create routers in the admin interface.'))
                
            return thresholds, routers
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error accessing database models: {str(e)}'))
            raise

    def check_influxdb_connection(self):
        """Test InfluxDB connection"""
        self.stdout.write(self.style.WARNING('\n=== 📈 INFLUXDB CONNECTION ==='))
        
        try:
            from api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            
            client = get_influx_client()
            if client is None:
                self.stdout.write(self.style.ERROR('❌ Failed to get InfluxDB client'))
                return None
            
            # Test connection with a simple query
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -1h)
            |> limit(n: 1)
            '''
            
            result = client.query_api().query(query, org=INFLUXDB_ORG)
            
            self.stdout.write(self.style.SUCCESS('✅ InfluxDB connection successful'))
            self.stdout.write(f'📊 Bucket: {INFLUXDB_BUCKET}')
            self.stdout.write(f'🏢 Organization: {INFLUXDB_ORG}')
            
            return client
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ InfluxDB connection failed: {str(e)}'))
            return None

    def check_thresholds_and_routers(self, router_filter=None):
        """Show detailed threshold and router configuration"""
        self.stdout.write(self.style.WARNING('\n=== ⚙️  THRESHOLD & ROUTER DETAILS ==='))
        
        try:
            from router_supervisor.core_models.models import Threshold, Router
            
            routers = Router.objects.all()
            if router_filter:
                routers = routers.filter(name__icontains=router_filter)
            
            for router in routers:
                self.stdout.write(f'\n🖥️  Router: {router.name}')
                self.stdout.write(f'   IP: {router.ip_address}')
                
                try:
                    threshold = router.threshold
                    self.stdout.write(f'   🎯 Thresholds:')
                    self.stdout.write(f'      CPU: {threshold.cpu}%')
                    self.stdout.write(f'      RAM: {threshold.ram}%') 
                    self.stdout.write(f'      Traffic: {threshold.traffic}%')
                    
                except Exception as e:
                    self.stdout.write(f'   ❌ No threshold assigned: {str(e)}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error checking thresholds: {str(e)}'))

    def check_recent_metrics(self, router_filter=None):
        """Check recent metrics in InfluxDB"""
        self.stdout.write(self.style.WARNING('\n=== 📊 RECENT METRICS CHECK ==='))
        
        try:
            from api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            from router_supervisor.core_models.models import Router
            
            client = get_influx_client()
            if not client:
                return
            
            routers = Router.objects.all()
            if router_filter:
                routers = routers.filter(name__icontains=router_filter)
            
            for router in routers:
                self.stdout.write(f'\n🔍 Checking metrics for router: {router.name}')
                
                # Check what measurements are available
                self.check_available_measurements(client, router.name)
                
                # Check specific metrics
                self.check_router_specific_metrics(client, router)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error checking metrics: {str(e)}'))

    def check_available_measurements(self, client, router_name):
        """Check what measurements are available in InfluxDB"""
        from api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        try:
            # Get sample of recent data
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -2h)
            |> limit(n: 20)
            '''
            
            result = client.query_api().query(query, org=INFLUXDB_ORG)
            
            measurements = set()
            fields = set()
            hosts = set()
            
            for table in result:
                for record in table.records:
                    measurements.add(record.get_measurement() or 'None')
                    fields.add(record.get_field() or 'None')
                    
                    # Check for router/host identification
                    values = record.values
                    if 'router' in values:
                        hosts.add(values['router'])
                    if 'host' in values:
                        hosts.add(values['host'])
                    if 'hostname' in values:
                        hosts.add(values['hostname'])
            
            self.stdout.write(f'   📋 Available measurements: {sorted(list(measurements))[:5]}...')
            self.stdout.write(f'   🏷️  Available fields: {sorted(list(fields))[:5]}...')
            self.stdout.write(f'   🏠 Available hosts: {sorted(list(hosts))}')
            
            # Check if our router appears in the data
            if router_name.lower() in [h.lower() for h in hosts]:
                self.stdout.write(f'   ✅ Router "{router_name}" found in data')
            else:
                self.stdout.write(f'   ❌ Router "{router_name}" NOT found in data')
                self.stdout.write(f'   💡 Available hosts: {sorted(list(hosts))}')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Error checking measurements: {str(e)}')

    def check_router_specific_metrics(self, client, router):
        """Check specific metrics for a router and compare with thresholds"""
        from api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        try:
            threshold = router.threshold
        except:
            self.stdout.write(f'   ⚠️  No threshold configured for {router.name}')
            return
        
        # Metrics to check with various possible field names
        metrics_config = [
            ('CPU', threshold.cpu, ['cpu_usage', 'cpu_percent', 'cpu', 'usage_active', 'cpu_usage_active']),
            ('RAM', threshold.ram, ['memory_usage', 'memory_percent', 'memory', 'mem_used_percent', 'usage_percent']),
            ('Traffic', threshold.traffic, ['interface_utilization', 'traffic', 'network_usage', 'interface_rx_bytes', 'interface_tx_bytes'])
        ]
        
        for metric_name, threshold_value, possible_fields in metrics_config:
            self.stdout.write(f'\n   🔍 {metric_name} (threshold: {threshold_value}%):')
            
            found_data = False
            for field_name in possible_fields:
                if self.check_specific_metric_field(client, router.name, field_name, threshold_value):
                    found_data = True
                    break
            
            if not found_data:
                self.stdout.write(f'      ❌ No recent data found for any {metric_name} fields')

    def check_specific_metric_field(self, client, router_name, field_name, threshold_value):
        """Check a specific field for a metric"""
        from api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        # Try multiple ways to identify the router
        router_filters = [
            f'|> filter(fn: (r) => r["router"] == "{router_name}")',
            f'|> filter(fn: (r) => r["host"] == "{router_name}")',
            f'|> filter(fn: (r) => r["hostname"] == "{router_name}")',
            f'|> filter(fn: (r) => r["router"] == "{router_name.lower()}")',
            f'|> filter(fn: (r) => r["host"] == "{router_name.lower()}")'
        ]
        
        for router_filter in router_filters:
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -30m)
            |> filter(fn: (r) => r._field == "{field_name}")
            {router_filter}
            |> last()
            '''
            
            try:
                result = client.query_api().query(query, org=INFLUXDB_ORG)
                
                if result:
                    for table in result:
                        for record in table.records:
                            current_value = record.get_value()
                            timestamp = record.get_time()
                            measurement = record.get_measurement()
                            
                            try:
                                value_num = float(current_value)
                                threshold_exceeded = value_num > float(threshold_value)
                                
                                status = "🔴 EXCEEDED" if threshold_exceeded else "✅ OK"
                                self.stdout.write(f'      {status} {field_name}: {value_num:.2f}% (vs {threshold_value}%)')
                                self.stdout.write(f'          Measurement: {measurement}, Time: {timestamp}')
                                
                                if threshold_exceeded:
                                    self.stdout.write(f'          ⚠️  ALERT: This should trigger an alert!')
                                
                                return True
                                
                            except (ValueError, TypeError):
                                self.stdout.write(f'      ⚠️  {field_name}: {current_value} (non-numeric)')
                                return True
                
            except Exception as e:
                continue  # Try next filter
        
        return False
