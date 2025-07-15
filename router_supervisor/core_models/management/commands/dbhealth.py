from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
from django.contrib.auth import get_user_model
import sys


class Command(BaseCommand):
    help = 'Check database health and report status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Running database health check...'))
        
        # Test database connection
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✓ Database connection: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection: FAILED - {e}'))
            return
        
        # Check if migrations are up to date
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.stdout.write(self.style.WARNING(f'⚠ Pending migrations found: {len(plan)} migrations need to be applied'))
                for migration in plan:
                    self.stdout.write(f'  - {migration[0].app_label}.{migration[0].name}')
            else:
                self.stdout.write(self.style.SUCCESS('✓ Migrations: All up to date'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Migration check: FAILED - {e}'))
        
        # Check if User model table exists and is accessible
        try:
            User = get_user_model()
            user_count = User.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✓ User model: OK ({user_count} users in database)'))
            
            # Check if any superuser exists
            superuser_count = User.objects.filter(is_superuser=True).count()
            if superuser_count > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ Superusers: {superuser_count} found'))
            else:
                self.stdout.write(self.style.WARNING('⚠ No superusers found - you may want to create one'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ User model: FAILED - {e}'))
        
        # Test some basic table operations
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✓ Database queries: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database queries: FAILED - {e}'))
        
        self.stdout.write(self.style.SUCCESS('Database health check completed!'))
