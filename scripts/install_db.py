#!/usr/bin/env python3
"""
Database installation and setup script for Router Supervisor
This script handles database initialization, migrations, and seed data
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

def setup_django():
    """Setup Django settings"""
    import sys
    import os
    
    # Use the corrected production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'router_supervisor.prod_settings')
    
    # Ensure PYTHONPATH includes the router_supervisor directory
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    django.setup()

def run_migrations():
    """Apply database migrations"""
    print("🔄 Applying database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations applied successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_superuser():
    """Create a default superuser if none exists"""
    print("👤 Setting up admin user...")
    try:
        # Try to use custom user model first, fall back to default User
        try:
            from core_models.models import CustomUser
            User = CustomUser
            print("ℹ️  Using CustomUser model")
        except ImportError:
            from django.contrib.auth.models import User
            print("ℹ️  Using default User model")
        
        if not User.objects.filter(is_superuser=True).exists():
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@telecom-sudparis.eu')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_user = os.environ.get('ADMIN_USER', 'admin')
            
            # Create user with appropriate fields
            user_data = {
                'username': admin_user,
                'email': admin_email,
                'password': admin_password,
            }
            
            # Add custom fields if using CustomUser
            if hasattr(User, 'nom'):
                user_data.update({
                    'nom': 'Administrator',
                    'prenom': 'System',
                    'role': 'admin'
                })
            
            user = User.objects.create_superuser(**user_data)
            print(f"✅ Superuser '{admin_user}' created successfully!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
        else:
            print("ℹ️  Superuser already exists, skipping creation")
        
        return True
    except Exception as e:
        print(f"❌ Superuser creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def seed_initial_data():
    """Load initial data for the application"""
    print("🌱 Loading initial data...")
    try:
        # Check if core_models app exists
        try:
            from core_models.models import (
                CustomUser, KPI, Seuil, Routeur, Interface, Alertes,
                UtilisateurRouteur, SeuilKPI
            )
            print("✅ Core models found, loading advanced data...")
            # Your existing core_models code here...
            return True
        except ImportError:
            print("ℹ️  Core models not available, loading basic data...")
            # Use existing thresholds_app models
            from thresholds_app.models import InterfaceThreshold
            
            # Create sample thresholds if none exist
            if not InterfaceThreshold.objects.exists():
                sample_thresholds = [
                    {
                        'interface_name': 'GigabitEthernet0/0/0',
                        'router_ip': '192.168.1.1',
                        'cpu_threshold': 80.0,
                        'memory_threshold': 85.0,
                        'bandwidth_threshold': 90.0,
                        'packet_loss_threshold': 5.0,
                    },
                    {
                        'interface_name': 'GigabitEthernet0/0/1',
                        'router_ip': '192.168.1.2',
                        'cpu_threshold': 75.0,
                        'memory_threshold': 80.0,
                        'bandwidth_threshold': 85.0,
                        'packet_loss_threshold': 3.0,
                    },
                ]
                
                for threshold_data in sample_thresholds:
                    InterfaceThreshold.objects.create(**threshold_data)
                
                print(f"✅ Created {len(sample_thresholds)} interface thresholds")
            else:
                print("ℹ️  Basic data already exists, skipping seed")
            
            return True
            
    except Exception as e:
        print(f"❌ Initial data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def collect_static_files():
    """Collect static files"""
    print("📁 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    print("🔌 Checking database connection...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🚀 Starting Router Supervisor Database Installation...")
    print("=" * 60)
    
    # Set up Django
    setup_django()
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Cannot proceed without successful migrations")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    # Seed initial data
    seed_initial_data()
    
    # Collect static files
    collect_static_files()
    
    print("=" * 60)
    print("🎉 Database installation completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Access the admin panel at: http://localhost/admin/")
    print("   2. Access the main dashboard at: http://localhost/")
    print("   3. Configure your router connections in the settings")
    print("=" * 60)

if __name__ == '__main__':
    main()
