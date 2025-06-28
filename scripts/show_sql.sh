#!/bin/bash
# Export Django models to SQL equivalent
# This shows you what Django creates based on your schema

cd /code

echo "🔄 Generating SQL equivalent of Django models..."
echo "=============================================="

# Generate SQL for the models (this shows what Django would create)
python3 router_supervisor/manage.py sqlmigrate core_models 0001 || echo "Migration not found, creating..."

echo ""
echo "📋 To see all SQL that Django will execute:"
echo "   python3 router_supervisor/manage.py sqlmigrate core_models 0001"
echo ""
echo "📋 To create custom SQL data:"
echo "   python3 router_supervisor/manage.py dbshell"
echo ""
echo "📋 Current database tables:"
python3 router_supervisor/manage.py dbshell -c "\dt"
