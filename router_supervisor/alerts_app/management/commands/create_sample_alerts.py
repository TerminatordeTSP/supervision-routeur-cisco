from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from router_supervisor.core_models.models import Router, Threshold
from alerts_app.models import AlertRule, AlertInstance
import random


User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample alert rules and test alerts'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample alert rules and test data...')
        
        # Get or create a router
        router, created = Router.objects.get_or_create(
            name='Test Router',
            defaults={
                'ip_address': '192.168.1.1',
                'username': 'admin',
                'password': 'admin',
                'secret': 'secret'
            }
        )
        
        if created:
            self.stdout.write(f'Created test router: {router.name}')
        
        # Create sample alert rules
        rules = [
            {
                'name': 'High CPU Usage',
                'description': 'Alert when CPU usage exceeds 80%',
                'metric': 'cpu',
                'condition': 'gt',
                'threshold_value': 80.0,
                'email_enabled': True,
            },
            {
                'name': 'High Memory Usage',
                'description': 'Alert when RAM usage exceeds 85%',
                'metric': 'ram',
                'condition': 'gt',
                'threshold_value': 85.0,
                'email_enabled': True,
            },
            {
                'name': 'High Traffic',
                'description': 'Alert when traffic exceeds 90%',
                'metric': 'traffic',
                'condition': 'gt',
                'threshold_value': 90.0,
                'email_enabled': False,
            }
        ]
        
        for rule_data in rules:
            rule, created = AlertRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f'Created alert rule: {rule.name}')
        
        # Create a test alert
        cpu_rule = AlertRule.objects.filter(metric='cpu').first()
        if cpu_rule:
            alert, created = AlertInstance.objects.get_or_create(
                rule=cpu_rule,
                router=router,
                defaults={
                    'severity': 'high',
                    'message': f'CPU usage (95%) exceeds threshold ({cpu_rule.threshold_value}%)',
                    'metric_value': 95.0,
                    'threshold_value': cpu_rule.threshold_value
                }
            )
            if created:
                self.stdout.write(f'Created test alert: {alert.rule.name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
