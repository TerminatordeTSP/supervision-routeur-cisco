from django.core.management.base import BaseCommand
from django.utils import timezone
from router_supervisor.alerts_app.models import AlertRule, AlertInstance
from router_supervisor.alerts_app.utils import check_thresholds_and_create_alerts
from router_supervisor.api_app.influx_utils import get_influx_client, INFLUXDB_BUCKET, INFLUXDB_ORG
from router_supervisor.core_models.models import Router
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create alerts for detected threshold violations'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'🚨 ALERT CREATION TEST at {timezone.now()}')
        )
        
        try:
            # Method 1: Use the existing alert creation system
            self.stdout.write('\n=== Testing existing alert system ===')
            initial_count = AlertInstance.objects.count()
            self.stdout.write(f'Initial alert count: {initial_count}')
            
            # Call the existing function
            check_thresholds_and_create_alerts()
            
            final_count = AlertInstance.objects.count()
            self.stdout.write(f'Final alert count: {final_count}')
            self.stdout.write(f'New alerts created: {final_count - initial_count}')
            
            # Method 2: Create alert manually with our known data
            self.stdout.write('\n=== Creating alert manually ===')
            
            client = get_influx_client()
            router = Router.objects.first()
            
            # Get CPU data
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
                    
                    # Find a matching alert rule
                    rule = AlertRule.objects.filter(
                        metric='cpu',
                        condition='gt',
                        threshold_value__lt=cpu_value,
                        is_active=True
                    ).first()
                    
                    if rule:
                        # Check if alert already exists
                        existing = AlertInstance.objects.filter(
                            rule=rule,
                            router=router,
                            status='active'
                        ).first()
                        
                        if not existing:
                            alert = AlertInstance.objects.create(
                                rule=rule,
                                router=router,
                                severity='medium',
                                message=f"CPU usage ({cpu_value}%) exceeds threshold ({rule.threshold_value}%)",
                                metric_value=cpu_value,
                                threshold_value=rule.threshold_value
                            )
                            
                            self.stdout.write(self.style.SUCCESS(f'✅ Created alert: {alert}'))
                        else:
                            self.stdout.write(f'⚠️  Alert already exists: {existing}')
                    else:
                        self.stdout.write(f'❌ No matching rule found for CPU {cpu_value}%')
                    break
            
            # Show final results
            self.stdout.write('\n=== FINAL RESULTS ===')
            total_alerts = AlertInstance.objects.count()
            self.stdout.write(f'Total alerts in database: {total_alerts}')
            
            if total_alerts > 0:
                self.stdout.write('\nRecent alerts:')
                for alert in AlertInstance.objects.all()[:5]:
                    self.stdout.write(f'  {alert}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            import traceback
            traceback.print_exc()
