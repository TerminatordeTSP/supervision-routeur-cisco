#!/usr/bin/env python3

import os
import sys
import django
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_django():
    """Configure Django settings"""
    sys.path.append('/code/router_supervisor')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'router_supervisor.prod_settings')
    django.setup()

def reset_database():
    """Supprime et recrée complètement la base de données"""
    print("🔄 Début de la réinitialisation COMPLÈTE de la base de données...")
    
    # Paramètres de connexion PostgreSQL
    connection_params = {
        'host': os.environ.get('SQL_HOST', 'db'),
        'port': os.environ.get('SQL_PORT', '5432'),
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        # Connexion à PostgreSQL (base postgres par défaut)
        conn = psycopg2.connect(database='postgres', **connection_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🗑️  Suppression complète de la base de données 'postgres'...")
        
        # Fermer toutes les connexions actives à la base
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'postgres'
              AND pid <> pg_backend_pid()
        """)
        
        # Supprimer et recréer la base de données
        cursor.execute('DROP DATABASE IF EXISTS postgres')
        cursor.execute('CREATE DATABASE postgres')
        
        print("✅ Base de données 'postgres' recréée avec succès!")
        
        cursor.close()
        conn.close()
        
        print("🚀 La base de données est maintenant complètement vide et prête!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        return False

if __name__ == "__main__":
    reset_database()
