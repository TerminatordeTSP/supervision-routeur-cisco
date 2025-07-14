#!/usr/bin/env python3
"""
Script pour réinitialiser les migrations Django
"""
import os
import sys
import django
from django.conf import settings
from django.db import connection

# Configuration Django
sys.path.append('/code/router_supervisor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'router_supervisor.prod_settings')
django.setup()

def reset_database():
    """Réinitialise complètement la base de données"""
    cursor = connection.cursor()
    
    try:
        print("🗑️  Suppression COMPLÈTE de toutes les tables...")
        
        # Supprimer TOUTES les tables de migration Django
        cursor.execute('DROP TABLE IF EXISTS django_migrations CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS django_content_type CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS auth_permission CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS auth_group CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS auth_group_permissions CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS auth_user CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS auth_user_groups CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS django_admin_log CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS django_session CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS "user" CASCADE;')  # Table user générique (avec guillemets)
        cursor.execute('DROP TABLE IF EXISTS django_migrations CASCADE;')
        print("   ✓ Tables système Django supprimées")
        
        # Supprimer les tables core_models
        cursor.execute('DROP TABLE IF EXISTS core_models_user CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS core_models_router CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS core_models_interface CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS core_models_metric CASCADE;')
        print("   ✓ Tables core_models supprimées")
        
        # Supprimer les anciennes tables d'alertes
        cursor.execute('DROP TABLE IF EXISTS alert CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS alerthistory CASCADE;')  
        cursor.execute('DROP TABLE IF EXISTS alertrule CASCADE;')
        print("   ✓ anciennes tables alert* supprimées")
        
        # Supprimer les nouvelles tables d'alertes si elles existent
        cursor.execute('DROP TABLE IF EXISTS alerts_alert CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS alerts_history CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS alerts_rule CASCADE;')
        print("   ✓ nouvelles tables alerts_* supprimées")
        
        # Supprimer les tables settings_app
        cursor.execute('DROP TABLE IF EXISTS settings_app_userpreferences CASCADE;')
        print("   ✓ Tables settings_app supprimées")
        
        print("✅ Nettoyage COMPLET de la base de données terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False
    
    return True

def main():
    print("🔄 Début de la réinitialisation des migrations...")
    
    if reset_database():
        print("🚀 La base de données est prête pour une nouvelle migration!")
    else:
        print("💥 Échec de la réinitialisation")
        sys.exit(1)

if __name__ == '__main__':
    main()
