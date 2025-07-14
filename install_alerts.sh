#!/bin/bash

# Script d'installation du système d'alertes pour router_supervisor

set -e

echo "🚀 Installation du système d'alertes pour router_supervisor"
echo "============================================================"

# Répertoire de base
BASE_DIR="/Users/paul/supervision-routeur-cisco"
ROUTER_SUPERVISOR_DIR="$BASE_DIR/router_supervisor"
VENV_PYTHON="$BASE_DIR/venv/bin/python"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "$ROUTER_SUPERVISOR_DIR" ]; then
    echo "❌ Erreur: Répertoire router_supervisor non trouvé"
    exit 1
fi

cd "$ROUTER_SUPERVISOR_DIR"

echo "📁 Répertoire de travail: $(pwd)"

# Vérifier l'environnement virtuel
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Erreur: Environnement virtuel non trouvé à $VENV_PYTHON"
    exit 1
fi

echo "🐍 Utilisation de Python: $VENV_PYTHON"

# Appliquer les migrations pour l'app core_models d'abord
echo "📦 Application des migrations core_models..."
PYTHONPATH="$ROUTER_SUPERVISOR_DIR" "$VENV_PYTHON" manage.py migrate core_models || echo "⚠️  Migrations core_models déjà appliquées ou erreur mineure"

# Appliquer les migrations pour l'app alerts_app
echo "📦 Application des migrations alerts_app..."
PYTHONPATH="$ROUTER_SUPERVISOR_DIR" "$VENV_PYTHON" manage.py migrate alerts_app || echo "⚠️  Migrations alerts_app déjà appliquées ou erreur mineure"

# Appliquer toutes les autres migrations
echo "📦 Application de toutes les migrations..."
PYTHONPATH="$ROUTER_SUPERVISOR_DIR" "$VENV_PYTHON" manage.py migrate || echo "⚠️  Certaines migrations pourraient avoir échoué"

# Créer un superutilisateur si nécessaire
echo "👤 Vérification du superutilisateur..."
PYTHONPATH="$ROUTER_SUPERVISOR_DIR" "$VENV_PYTHON" -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Création d\\'un superutilisateur admin/admin...')
    User.objects.create_superuser('admin@admin.com', 'admin', first_name='Admin', last_name='User', role='admin')
    print('✅ Superutilisateur créé: admin@admin.com / admin')
else:
    print('✅ Superutilisateur déjà existant')
" || echo "⚠️  Problème avec la création du superutilisateur"

# Configurer le système d'alertes
echo "⚙️  Configuration du système d'alertes..."
PYTHONPATH="$ROUTER_SUPERVISOR_DIR" "$VENV_PYTHON" -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from router_supervisor.core_models.models import Router, Threshold, KPI, Interface
from router_supervisor.alerts_app.models import AlertRule, Alert, AlertSeverity, AlertType
from router_supervisor.alerts_app.services import AlertService
from django.utils import timezone
from decimal import Decimal
import random

print('📊 Configuration des données de base...')

# Créer des KPIs de base
kpis_data = [
    'CPU', 'RAM', 'Traffic', 'Interface Traffic', 'Interface Errors'
]

for kpi_name in kpis_data:
    kpi, created = KPI.objects.get_or_create(name=kpi_name)
    if created:
        print(f'  ✅ KPI créé: {kpi_name}')

# Créer des seuils de base si aucun n'existe
if not Threshold.objects.exists():
    thresholds_data = [
        {'name': 'Seuil Standard', 'cpu': 80, 'ram': 1024, 'traffic': 100},
        {'name': 'Seuil Élevé', 'cpu': 90, 'ram': 2048, 'traffic': 200},
        {'name': 'Seuil Critique', 'cpu': 95, 'ram': 4096, 'traffic': 500},
    ]
    
    for threshold_data in thresholds_data:
        threshold = Threshold.objects.create(**threshold_data)
        print(f'  ✅ Seuil créé: {threshold.name}')

# Créer un routeur de test si aucun n'existe
if not Router.objects.exists():
    threshold = Threshold.objects.first()
    router = Router.objects.create(
        name='Routeur-Test-01',
        ip_address='192.168.1.1',
        username='admin',
        password='password',
        secret='secret',
        threshold=threshold
    )
    print(f'  ✅ Routeur de test créé: {router.name}')
    
    # Créer une interface par défaut
    interface = Interface.objects.create(
        name='GigabitEthernet0/0',
        traffic=50.0,
        router=router,
        status='up',
        input_rate=25.0,
        output_rate=25.0,
        errors=0
    )
    print(f'  ✅ Interface créée: {interface.name}')

# Assigner des seuils aux routeurs sans seuils
routers_without_thresholds = Router.objects.filter(threshold__isnull=True)
for router in routers_without_thresholds:
    threshold = Threshold.objects.first()
    router.threshold = threshold
    router.save()
    print(f'  ✅ Seuil assigné au routeur: {router.name}')

# Créer quelques règles d'alertes
kpis = {kpi.name: kpi for kpi in KPI.objects.all()}

rules_data = [
    {
        'name': 'CPU Critique Global',
        'description': 'Alerte critique quand le CPU dépasse 95%',
        'kpi': kpis.get('CPU'),
        'operator': 'gt',
        'threshold_value': Decimal('95'),
        'severity': AlertSeverity.CRITICAL,
        'alert_type': AlertType.THRESHOLD,
        'cooldown_minutes': 2,
    },
    {
        'name': 'Mémoire Élevée',
        'description': 'Alerte quand la mémoire dépasse 3GB',
        'kpi': kpis.get('RAM'),
        'operator': 'gt',
        'threshold_value': Decimal('3072'),
        'severity': AlertSeverity.HIGH,
        'alert_type': AlertType.THRESHOLD,
        'cooldown_minutes': 5,
    },
]

for rule_data in rules_data:
    if rule_data['kpi']:
        rule, created = AlertRule.objects.get_or_create(
            name=rule_data['name'],
            kpi=rule_data['kpi'],
            defaults=rule_data
        )
        if created:
            print(f'  ✅ Règle d\\'alerte créée: {rule.name}')

# Créer quelques alertes de test
router = Router.objects.first()
if router and not Alert.objects.exists():
    test_alerts = [
        {
            'title': 'Test: CPU Critique sur ' + router.name,
            'description': 'Alerte de test pour démonstration du système',
            'metric_name': 'CPU',
            'current_value': Decimal('98.5'),
            'threshold_value': Decimal('95.0'),
            'unit': '%',
            'severity': AlertSeverity.CRITICAL,
        },
        {
            'title': 'Test: Mémoire Élevée sur ' + router.name,
            'description': 'Utilisation mémoire au-dessus du seuil normal',
            'metric_name': 'RAM',
            'current_value': Decimal('3500'),
            'threshold_value': Decimal('3072'),
            'unit': 'MB',
            'severity': AlertSeverity.HIGH,
        },
        {
            'title': 'Test: Trafic Modéré sur ' + router.name,
            'description': 'Trafic réseau légèrement élevé',
            'metric_name': 'Traffic',
            'current_value': Decimal('125'),
            'threshold_value': Decimal('100'),
            'unit': 'Mbps',
            'severity': AlertSeverity.MEDIUM,
        },
    ]
    
    for alert_data in test_alerts:
        alert = Alert.objects.create(
            router=router,
            kpi=kpis.get(alert_data['metric_name']),
            threshold=router.threshold,
            alert_type=AlertType.THRESHOLD,
            **alert_data
        )
        print(f'  ✅ Alerte de test créée: {alert.title}')

print('\\n🎉 Configuration du système d\\'alertes terminée!')
print('   📊 Accédez au dashboard des alertes: http://localhost:8000/alerts/')
print('   🔧 Admin interface: http://localhost:8000/admin/')

" || echo "⚠️  Erreur lors de la configuration des données"

echo ""
echo "✅ Installation terminée!"
echo ""
echo "🌐 Pour démarrer le serveur de développement:"
echo "   cd $ROUTER_SUPERVISOR_DIR"
echo "   PYTHONPATH=$ROUTER_SUPERVISOR_DIR $VENV_PYTHON manage.py runserver"
echo ""
echo "📊 URLs disponibles:"
echo "   • Dashboard principal: http://localhost:8000/"
echo "   • Dashboard des alertes: http://localhost:8000/alerts/"
echo "   • Liste des alertes: http://localhost:8000/alerts/list/"
echo "   • Administration: http://localhost:8000/admin/"
echo ""
echo "👤 Connexion admin:"
echo "   • Email: admin@admin.com"
echo "   • Mot de passe: admin"
echo ""
