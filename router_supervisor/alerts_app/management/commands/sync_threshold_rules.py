from django.core.management.base import BaseCommand
from router_supervisor.core_models.models import Threshold
from router_supervisor.alerts_app.models import AlertRule


class Command(BaseCommand):
    help = 'Synchronize alert rules from existing thresholds'

    def handle(self, *args, **options):
        self.stdout.write('Starting threshold to alert rules synchronization...')
        
        # Get all existing thresholds
        thresholds = Threshold.objects.all()
        
        synced_count = 0
        created_count = 0
        
        for threshold in thresholds:
            # Create alert rules for each metric type in the threshold
            metrics = [
                ('cpu', threshold.cpu),
                ('ram', threshold.ram), 
                ('traffic', threshold.traffic)
            ]
            
            for metric_name, threshold_value in metrics:
                if threshold_value > 0:  # Only create rules for thresholds > 0
                    rule_name = f"{threshold.name} - {metric_name.upper()}"
                    
                    # Check if rule already exists
                    existing_rule = AlertRule.objects.filter(
                        name=rule_name,
                        metric=metric_name
                    ).first()
                    
                    if existing_rule:
                        # Update existing rule
                        existing_rule.threshold_value = threshold_value
                        existing_rule.description = f"Auto-generated from threshold '{threshold.name}'"
                        existing_rule.save()
                        synced_count += 1
                        self.stdout.write(f"  ↻ Updated: {rule_name}")
                    else:
                        # Create new rule
                        AlertRule.objects.create(
                            name=rule_name,
                            description=f"Auto-generated from threshold '{threshold.name}'",
                            metric=metric_name,
                            condition='gt',  # Greater than condition for thresholds
                            threshold_value=threshold_value,
                            is_active=True,
                            email_enabled=True,
                            email_recipients=''  # Can be configured later
                        )
                        created_count += 1
                        self.stdout.write(f"  ✓ Created: {rule_name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Synchronization completed: {created_count} rules created, {synced_count} rules updated'
            )
        )
