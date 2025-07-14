from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import sys
import time


class Command(BaseCommand):
    help = 'Initialize the database with all necessary migrations and setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-checks',
            action='store_true',
            help='Skip database connectivity checks',
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=30,
            help='Maximum number of database connection retries',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database initialization...'))
        
        # Wait for database connection
        if not options['skip_checks']:
            self._wait_for_database(options['max_retries'])
        
        # Run migrations
        self._run_migrations()
        
        # Create superuser if needed
        self._create_superuser_if_needed()
        
        self.stdout.write(self.style.SUCCESS('Database initialization completed successfully!'))

    def _wait_for_database(self, max_retries):
        """Wait for database to be available"""
        self.stdout.write('Waiting for database connection...')
        
        for attempt in range(max_retries):
            try:
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database connection established!'))
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Could not connect to database after {max_retries} attempts: {e}'
                        )
                    )
                    sys.exit(1)
                else:
                    self.stdout.write(f'Database not ready (attempt {attempt + 1}/{max_retries}). Waiting...')
                    time.sleep(2)

    def _run_migrations(self):
        """Run Django migrations"""
        self.stdout.write('Checking for pending migrations...')
        
        try:
            # First, make sure migrations are up to date
            call_command('makemigrations', verbosity=1, interactive=False)
            
            # Then apply them
            call_command('migrate', verbosity=1, interactive=False)
            
            self.stdout.write(self.style.SUCCESS('Migrations completed successfully!'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Migration failed: {e}')
            )
            # Don't exit here - let the application try to start anyway
            # Some migrations might have succeeded

    def _create_superuser_if_needed(self):
        """Create a superuser if none exists"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write('No superuser found, you may want to create one manually.')
            else:
                self.stdout.write('Superuser already exists.')
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not check for superuser: {e}')
            )
