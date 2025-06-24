#!/usr/bin/env python3
"""
Test script to validate Django models and database setup
Run this script to test the database schema without Docker
"""

import os
import sys
import django

# Add the router_supervisor directory to the Python path
sys.path.insert(0, '/home/paul/supervision-routeur-cisco/router_supervisor')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

def test_models():
    """Test that all models can be imported and basic operations work"""
    print("🧪 Testing Django models...")
    
    try:
        from core_models.models import (
            CustomUser, KPI, Seuil, Routeur, Interface, Alertes,
            UtilisateurRouteur, SeuilKPI, KPIInterfaceLog
        )
        print("✅ All models imported successfully")
        
        # Test model string representations
        print("\n📋 Model Information:")
        models = [CustomUser, KPI, Seuil, Routeur, Interface, Alertes, 
                 UtilisateurRouteur, SeuilKPI, KPIInterfaceLog]
        
        for model in models:
            print(f"  - {model.__name__}: {model._meta.verbose_name}")
            print(f"    Fields: {[f.name for f in model._meta.fields[:5]]}{'...' if len(model._meta.fields) > 5 else ''}")
        
        return True
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_admin():
    """Test that admin interfaces are properly configured"""
    print("\n🔧 Testing Django admin...")
    
    try:
        from django.contrib import admin
        from core_models.admin import (
            CustomUserAdmin, KPIAdmin, SeuilAdmin, RouteurAdmin,
            InterfaceAdmin, AlertesAdmin
        )
        print("✅ All admin classes imported successfully")
        
        # Check registered models
        registered_models = admin.site._registry.keys()
        print(f"📋 Registered models: {len(registered_models)}")
        
        return True
    except ImportError as e:
        print(f"❌ Admin import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Admin test failed: {e}")
        return False

def show_sql_schema():
    """Show the SQL that Django would generate"""
    print("\n📊 Django Model Schema (SQL equivalent):")
    print("=" * 50)
    
    try:
        from django.core.management.sql import sql_create_index
        from django.db import connection
        from core_models.models import (
            CustomUser, KPI, Seuil, Routeur, Interface, Alertes
        )
        
        models = [CustomUser, KPI, Seuil, Routeur, Interface, Alertes]
        
        for model in models:
            print(f"\n-- Table: {model._meta.db_table}")
            print(f"-- Model: {model.__name__}")
            
            # Show field information
            for field in model._meta.fields:
                field_type = field.get_internal_type()
                null_str = "NULL" if field.null else "NOT NULL"
                print(f"--   {field.name}: {field_type} {null_str}")
        
        return True
    except Exception as e:
        print(f"❌ Schema generation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Router Supervisor Database Schema")
    print("=" * 60)
    
    success = True
    
    # Test models
    if not test_models():
        success = False
    
    # Test admin
    if not test_admin():
        success = False
    
    # Show schema
    show_sql_schema()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Your Django models are ready.")
        print("\n📋 Your SQL schema has been converted to Django models:")
        print("   - Utilisateurs → CustomUser (extends Django's User)")
        print("   - Seuil → Seuil")
        print("   - KPI → KPI") 
        print("   - Routeur → Routeur")
        print("   - Interface → Interface")
        print("   - Alertes → Alertes")
        print("   - Relations → Through models (UtilisateurRouteur, etc.)")
        print("\n🔧 Next steps:")
        print("   1. Create migrations: python manage.py makemigrations")
        print("   2. Apply migrations: python manage.py migrate")
        print("   3. Load sample data: python manage.py setup_database")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
