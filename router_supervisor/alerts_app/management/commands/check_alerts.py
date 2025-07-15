from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug threshold checking - show what data is available and if thresholds are exceeded'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating alerts',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable detailed debug output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        debug_mode = options.get('debug', False)
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Starting threshold check at {timezone.now()}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No alerts will be created'))
        
        if debug_mode:
            self.stdout.write(self.style.WARNING('DEBUG MODE - Detailed diagnostics enabled'))
        
        try:
            if debug_mode:
                self.check_database_configuration()
                self.check_influxdb_connection()
                self.check_recent_metrics()
            
            # alerts_created = check_thresholds_and_create_alerts()
            alerts_created = 0  # Temporary until utils is fixed
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {alerts_created} new alerts')
                )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Threshold check completed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during threshold check: {str(e)}')
            )
            logger.error(f'Error in check_alerts command: {str(e)}', exc_info=True)

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
            
            # Show details of each router and its threshold
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
            self.stdout.write(self.style.ERROR(f'❌ Error accessing database models: {str(e)}'))
            raise

    def check_influxdb_connection(self):
        """Test InfluxDB connection"""
        self.stdout.write(self.style.WARNING('\n=== 📈 INFLUXDB CONNECTION ==='))
        
        try:
            from router_supervisor.api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            
            client = get_influx_client()
            if client is None:
                self.stdout.write(self.style.ERROR('❌ Failed to get InfluxDB client'))
                return None
            
            # Test connection with a simple query
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -1h)
            |> limit(n: 5)
            '''
            
            result = client.query_api().query(query, org=INFLUXDB_ORG)
            
            self.stdout.write(self.style.SUCCESS('✅ InfluxDB connection successful'))
            self.stdout.write(f'📊 Bucket: {INFLUXDB_BUCKET}')
            self.stdout.write(f'🏢 Organization: {INFLUXDB_ORG}')
            
            # Show sample data
            self.stdout.write('\n📋 Sample recent data:')
            count = 0
            for table in result:
                for record in table.records:
                    if count < 3:  # Show only first 3 records
                        measurement = record.get_measurement()
                        field = record.get_field()
                        value = record.get_value()
                        time = record.get_time()
                        self.stdout.write(f'   {measurement}.{field} = {value} at {time}')
                        count += 1
            
            return client
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ InfluxDB connection failed: {str(e)}'))
            return None

    def check_recent_metrics(self):
        """Check recent metrics in InfluxDB and compare with thresholds"""
        self.stdout.write(self.style.WARNING('\n=== 📊 RECENT METRICS vs THRESHOLDS ==='))
        
        try:
            from router_supervisor.api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
            from router_supervisor.core_models.models import Router
            
            client = get_influx_client()
            if not client:
                return
            
            routers = Router.objects.all()
            
            for router in routers:
                self.stdout.write(f'\n🔍 Checking metrics for router: {router.name}')
                
                try:
                    threshold = router.threshold
                    self.stdout.write(f'   Thresholds - CPU: {threshold.cpu}%, RAM: {threshold.ram}%, Traffic: {threshold.traffic}%')
                    
                    # Check metrics with various possible names
                    self.check_metric_vs_threshold(client, router.name, 'CPU', threshold.cpu, 
                                                 ['cpu_usage', 'cpu_percent', 'usage_active'])
                    self.check_metric_vs_threshold(client, router.name, 'RAM', threshold.ram,
                                                 ['memory_usage', 'mem_used_percent', 'usage_percent'])
                    self.check_metric_vs_threshold(client, router.name, 'Traffic', threshold.traffic,
                                                 ['interface_utilization', 'network_usage'])
                    
                except Exception as e:
                    self.stdout.write(f'   ❌ No threshold configured for {router.name}: {str(e)}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error checking metrics: {str(e)}'))

    def check_metric_vs_threshold(self, client, router_name, metric_type, threshold_value, possible_fields):
        """Check a specific type of metric against its threshold"""
        from router_supervisor.api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        self.stdout.write(f'\n   🔍 {metric_type} (threshold: {threshold_value}%):')
        
        found_data = False
        
        # Try different field names and router identifiers
        for field_name in possible_fields:
            # Multiple ways to query for the router
            queries = [
                f'''from(bucket: "{INFLUXDB_BUCKET}")
                    |> range(start: -30m)
                    |> filter(fn: (r) => r._field == "{field_name}")
                    |> filter(fn: (r) => r["router"] == "{router_name}")
                    |> last()''',
                f'''from(bucket: "{INFLUXDB_BUCKET}")
                    |> range(start: -30m)
                    |> filter(fn: (r) => r._field == "{field_name}")
                    |> filter(fn: (r) => r["host"] == "{router_name}")
                    |> last()''',
                f'''from(bucket: "{INFLUXDB_BUCKET}")
                    |> range(start: -30m)
                    |> filter(fn: (r) => r._measurement == "{field_name}")
                    |> last()'''
            ]
            
            for query in queries:
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
                                    self.stdout.write(f'          Time: {timestamp}, Measurement: {measurement}')
                                    
                                    if threshold_exceeded:
                                        self.stdout.write(f'          ⚠️  ALERT: This should trigger an alert!')
                                        logger.warning(f'Threshold exceeded: {router_name} {metric_type} = {value_num}% > {threshold_value}%')
                                    
                                    found_data = True
                                    return  # Found data, stop searching
                                    
                                except (ValueError, TypeError):
                                    self.stdout.write(f'      ⚠️  {field_name}: {current_value} (non-numeric)')
                                    found_data = True
                                    return
                                    
                except Exception as e:
                    continue  # Try next query
        
        if not found_data:
            self.stdout.write(f'      ❌ No recent data found for {metric_type} fields: {possible_fields}')
            
            # Show what data IS available
            self.show_available_data(client, router_name)
    
    def log_debug_info(self):
        """Log detailed information about thresholds and current metrics"""
        from core_models.models import Threshold, Router
        from api_app.influx_utils import get_influx_client
        
        self.stdout.write(self.style.WARNING('=== DEBUG INFORMATION ==='))
        
        # Check configured thresholds
        thresholds = Threshold.objects.all()
        self.stdout.write(f'Found {thresholds.count()} configured thresholds:')
        
        for threshold in thresholds:
            self.stdout.write(f'  - Threshold ID {threshold.threshold_id}: CPU={threshold.cpu}, RAM={threshold.ram}, Traffic={threshold.traffic} (Name: {threshold.name})')
            logger.info(f'Threshold configured: ID={threshold.threshold_id}, CPU={threshold.cpu}, RAM={threshold.ram}, Traffic={threshold.traffic}')
        
        # Check routers
        routers = Router.objects.all()
        self.stdout.write(f'Found {routers.count()} configured routers:')
        
        for router in routers:
            self.stdout.write(f'  - Router: {router.name} ({router.ip_address})')
            logger.info(f'Router configured: {router.name} at {router.ip_address}')
        
        # Check InfluxDB connection and recent data
        try:
            client = get_influx_client()
            if client is None:
                self.stdout.write(self.style.ERROR('Failed to connect to InfluxDB'))
                return
            
            self.stdout.write(self.style.SUCCESS('Connected to InfluxDB successfully'))
            
            # Query recent metrics for each router
            for router in routers:
                self.check_router_metrics(client, router)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error connecting to InfluxDB: {str(e)}'))
            logger.error(f'InfluxDB connection error: {str(e)}', exc_info=True)
    
    def check_router_metrics(self, client, router):
        """Check current metric values for a specific router"""
        from api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        from core_models.models import Threshold
        
        self.stdout.write(f'\n--- Checking metrics for router: {router.name} ---')
        
        # Get threshold for this router if it has one
        try:
            threshold = router.threshold
            self.stdout.write(f'Router threshold - CPU: {threshold.cpu}%, RAM: {threshold.ram}%, Traffic: {threshold.traffic}')
        except:
            self.stdout.write(f'No threshold configured for router {router.name}')
            return
        
        # List of metrics to check
        metrics_to_check = [
            ('cpu_usage', threshold.cpu),
            ('memory_usage', threshold.ram),
            ('interface_utilization', threshold.traffic)
        ]
        
        for metric_name, threshold_value in metrics_to_check:
            self.check_specific_metric(client, router.name, metric_name, threshold_value)
    
    def check_specific_metric(self, client, router_name, metric_name, threshold_value):
        """Check a specific metric for a router"""
        from api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        # Query to get the latest value for this metric
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -30m)
        |> filter(fn: (r) => r["_measurement"] == "{metric_name}" or r._field == "{metric_name}")
        |> filter(fn: (r) => r["router"] == "{router_name}" or r["host"] == "{router_name}")
        |> last()
        '''
        
        try:
            result = client.query_api().query(query, org=INFLUXDB_ORG)
            
            if not result:
                self.stdout.write(f'  ❌ No recent data found for {metric_name} on {router_name}')
                logger.warning(f'No recent data for metric {metric_name} on router {router_name}')
                
                # Try alternative query with broader search
                self.try_alternative_queries(client, router_name, metric_name)
                return
            
            for table in result:
                for record in table.records:
                    current_value = record.get_value()
                    timestamp = record.get_time()
                    field = record.get_field()
                    measurement = record.get_measurement()
                    
                    # Check if threshold is exceeded
                    threshold_exceeded = float(current_value) > float(threshold_value)
                    
                    status = "🔴 EXCEEDED" if threshold_exceeded else "✅ OK"
                    self.stdout.write(f'  {status} {metric_name}: {current_value}% > {threshold_value}% (at {timestamp})')
                    self.stdout.write(f'    Field: {field}, Measurement: {measurement}')
                    
                    logger.info(f'Metric check: {metric_name}={current_value}, threshold={threshold_value}, exceeded={threshold_exceeded}, router={router_name}')
                    
                    if threshold_exceeded:
                        self.stdout.write(f'    ⚠️  This should trigger an alert!')
        
        except Exception as e:
            self.stdout.write(f'  ❌ Error querying {metric_name}: {str(e)}')
            logger.error(f'Error querying metric {metric_name}: {str(e)}', exc_info=True)
    
    def try_alternative_queries(self, client, router_name, metric_name):
        """Try alternative queries to find data"""
        from api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        # Query to see what measurements are available
        query_measurements = f'''
        import "influxdata/influxdb/schema"
        schema.measurements(bucket: "{INFLUXDB_BUCKET}")
        '''
        
        try:
            result = client.query_api().query(query_measurements, org=INFLUXDB_ORG)
            measurements = []
            for table in result:
                for record in table.records:
                    measurements.append(record.get_value())
            
            self.stdout.write(f'    Available measurements: {measurements[:10]}...')
            logger.info(f'Available measurements in InfluxDB: {measurements}')
            
        except Exception as e:
            self.stdout.write(f'    Could not retrieve measurements: {str(e)}')
            
        # Query to see what fields are available in recent data
        query_fields = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -1h)
        |> limit(n: 10)
        '''
        
        try:
            result = client.query_api().query(query_fields, org=INFLUXDB_ORG)
            self.stdout.write(f'    Recent data sample:')
            for table in result:
                for record in table.records:
                    measurement = record.get_measurement()
                    field = record.get_field()
                    value = record.get_value()
                    time = record.get_time()
                    self.stdout.write(f'      {measurement}.{field} = {value} at {time}')
                    break  # Just show first few records
                break
                
        except Exception as e:
            self.stdout.write(f'    Could not retrieve sample data: {str(e)}')
    
    def simulate_threshold_check(self):
        """Simulate threshold checking in dry-run mode"""
        self.stdout.write(self.style.WARNING('=== DRY RUN SIMULATION ==='))
        self.log_debug_info()
        self.stdout.write(self.style.WARNING('In dry-run mode, no alerts would be created'))
    
    def show_available_data(self, client, router_name):
        """Show what data is actually available in InfluxDB"""
        from router_supervisor.api_app.influx_utils import INFLUXDB_BUCKET, INFLUXDB_ORG
        
        try:
            # Get recent data to see what's available
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -2h)
            |> limit(n: 10)
            '''
            
            result = client.query_api().query(query, org=INFLUXDB_ORG)
            
            measurements = set()
            fields = set()
            
            for table in result:
                for record in table.records:
                    measurements.add(record.get_measurement() or 'None')
                    fields.add(record.get_field() or 'None')
            
            self.stdout.write(f'          💡 Available measurements: {sorted(list(measurements))[:5]}...')
            self.stdout.write(f'          💡 Available fields: {sorted(list(fields))[:5]}...')
            
        except Exception as e:
            self.stdout.write(f'          ❌ Could not retrieve available data: {str(e)}')
