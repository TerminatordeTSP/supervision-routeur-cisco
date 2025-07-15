#!/usr/bin/env python3
"""
Simple sync script to create alert rules from thresholds
Run this from within the Django container
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/code/router_supervisor')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# Configure Django
django.setup()

def sync_threshold_rules():
    from router_supervisor.core_models.models import Threshold
    from django.db import connection
    
    print('Starting threshold to alert rules synchronization...')
    
    # Get all existing thresholds
    thresholds = Threshold.objects.all()
    
    synced_count = 0
    created_count = 0
    
    with connection.cursor() as cursor:
        # Check if alert_rule table exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'alert_rule'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("Alert rule table doesn't exist. Creating it...")
            # Create the table manually
            cursor.execute("""
                CREATE TABLE alert_rule (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT DEFAULT '',
                    metric VARCHAR(20) NOT NULL,
                    condition VARCHAR(3) DEFAULT 'gt',
                    threshold_value FLOAT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    email_enabled BOOLEAN DEFAULT TRUE,
                    email_recipients TEXT DEFAULT ''
                )
            """)
            print("Alert rule table created.")
        
        for threshold in thresholds:
            # Create alert rules for each metric type in the threshold
            metrics = [
                ('cpu', threshold.cpu),
                ('ram', threshold.ram), 
                ('traffic', threshold.traffic)
            ]
            
            for metric, value in metrics:
                if value and value > 0:
                    rule_name = f"{threshold.name} - {metric.upper()}"
                    
                    # Check if rule already exists
                    cursor.execute("""
                        SELECT COUNT(*) FROM alert_rule 
                        WHERE name = %s AND metric = %s AND threshold_value = %s
                    """, [rule_name, metric, value])
                    
                    if cursor.fetchone()[0] == 0:
                        # Create new rule
                        cursor.execute("""
                            INSERT INTO alert_rule (name, description, metric, condition, threshold_value, is_active, email_enabled, email_recipients, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, [
                            rule_name,
                            f"Auto-generated rule from threshold: {threshold.name}",
                            metric,
                            'gt',  # Greater than condition by default
                            value,
                            True,  # is_active
                            True,  # email_enabled
                            ''     # email_recipients (empty by default)
                        ])
                        created_count += 1
                        print(f"Created rule: {rule_name}")
                    else:
                        synced_count += 1
    
    print(f"Synchronization completed!")
    print(f"Rules created: {created_count}")
    print(f"Rules already existing: {synced_count}")

if __name__ == "__main__":
    sync_threshold_rules()
