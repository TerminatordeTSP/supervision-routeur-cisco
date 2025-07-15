from django.core.management.base import BaseCommand
from django.utils import timezone
from alerts_app.utils import check_thresholds_and_create_alerts
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check thresholds and create alerts for metrics that exceed them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating alerts',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting threshold check at {timezone.now()}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No alerts will be created'))
        
        try:
            if not dry_run:
                check_thresholds_and_create_alerts()
            
            self.stdout.write(
                self.style.SUCCESS('Threshold check completed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during threshold check: {str(e)}')
            )
            logger.error(f'Error in check_alerts command: {str(e)}', exc_info=True)
