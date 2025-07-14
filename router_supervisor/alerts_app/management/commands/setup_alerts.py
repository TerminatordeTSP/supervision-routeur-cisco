from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from router_supervisor.core_models.models import Router, Threshold, KPI, Interface
from router_supervisor.alerts_app.models import AlertRule, AlertSeverity, AlertType
from router_supervisor.alerts_app.services import AlertService
import random


class Command(BaseCommand):
    help = 'Configure le système d\'alertes avec des données de test'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-thresholds',
            action='store_true',
            help='Créer des seuils par défaut pour les routeurs existants'
        )
        parser.add_argument(
            '--create-rules',
            action='store_true',
            help='Créer des règles d\'alertes personnalisées'
        )
        parser.add_argument(
            '--create-test-alerts',
            action='store_true',
            help='Créer quelques alertes de test'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Exécuter toutes les actions'
        )

    def handle(self, *args, **options):
        if options['all']:
            options['create_thresholds'] = True
            options['create_rules'] = True
            options['create_test_alerts'] = True

        if options['create_thresholds']:
            self.create_default_thresholds()

        if options['create_rules']:
            self.create_alert_rules()

        if options['create_test_alerts']:
            self.create_test_alerts()

        self.stdout.write(
            self.style.SUCCESS('Configuration du système d\'alertes terminée!')
        )

    def create_default_thresholds(self):
        """Créer des seuils par défaut pour les routeurs sans seuils"""
        self.stdout.write('Création des seuils par défaut...')
        
        # Créer des seuils par défaut
        default_thresholds = [
            {'name': 'Seuil Standard', 'cpu': 80, 'ram': 1024, 'traffic': 100},
            {'name': 'Seuil Élevé', 'cpu': 90, 'ram': 2048, 'traffic': 200},
            {'name': 'Seuil Critique', 'cpu': 95, 'ram': 4096, 'traffic': 500},
        ]
        
        created_thresholds = []
        for threshold_data in default_thresholds:
            threshold, created = Threshold.objects.get_or_create(
                name=threshold_data['name'],
                defaults=threshold_data
            )
            if created:
                created_thresholds.append(threshold)
                self.stdout.write(f'  ✓ Seuil créé: {threshold.name}')

        # Assigner des seuils aux routeurs qui n'en ont pas
        routers_without_thresholds = Router.objects.filter(threshold__isnull=True)
        for router in routers_without_thresholds:
            # Assigner un seuil aléatoire
            threshold = random.choice(created_thresholds or list(Threshold.objects.all()))
            router.threshold = threshold
            router.save()
            self.stdout.write(f'  ✓ Seuil assigné au routeur {router.name}: {threshold.name}')

    def create_alert_rules(self):
        """Créer des règles d'alertes personnalisées"""
        self.stdout.write('Création des règles d\'alertes...')
        
        # S'assurer que les KPIs existent
        kpis = {}
        for kpi_name in ['CPU', 'RAM', 'Traffic', 'Interface Traffic', 'Interface Errors']:
            kpi, created = KPI.objects.get_or_create(name=kpi_name)
            kpis[kpi_name] = kpi
            if created:
                self.stdout.write(f'  ✓ KPI créé: {kpi_name}')

        # Définir les règles d'alertes
        rules_data = [
            {
                'name': 'CPU Critique Global',
                'description': 'Alerte critique quand le CPU dépasse 95%',
                'kpi': kpis['CPU'],
                'operator': 'gt',
                'threshold_value': 95,
                'severity': AlertSeverity.CRITICAL,
                'alert_type': AlertType.THRESHOLD,
                'cooldown_minutes': 2,
            },
            {
                'name': 'Mémoire Élevée',
                'description': 'Alerte quand la mémoire dépasse 3GB',
                'kpi': kpis['RAM'],
                'operator': 'gt',
                'threshold_value': 3072,
                'severity': AlertSeverity.HIGH,
                'alert_type': AlertType.THRESHOLD,
                'cooldown_minutes': 5,
            },
            {
                'name': 'Trafic Anormal',
                'description': 'Alerte quand le trafic dépasse 300 Mbps',
                'kpi': kpis['Traffic'],
                'operator': 'gt',
                'threshold_value': 300,
                'severity': AlertSeverity.MEDIUM,
                'alert_type': AlertType.THRESHOLD,
                'cooldown_minutes': 10,
            },
            {
                'name': 'Erreurs Interface',
                'description': 'Alerte quand il y a plus de 10 erreurs sur une interface',
                'kpi': kpis['Interface Errors'],
                'operator': 'gt',
                'threshold_value': 10,
                'severity': AlertSeverity.HIGH,
                'alert_type': AlertType.HIGH_ERROR_RATE,
                'cooldown_minutes': 5,
            },
        ]

        for rule_data in rules_data:
            rule, created = AlertRule.objects.get_or_create(
                name=rule_data['name'],
                kpi=rule_data['kpi'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f'  ✓ Règle créée: {rule.name}')

    def create_test_alerts(self):
        """Créer quelques alertes de test"""
        self.stdout.write('Création d\'alertes de test...')
        
        routers = list(Router.objects.all())
        if not routers:
            self.stdout.write(
                self.style.WARNING('Aucun routeur trouvé. Créez d\'abord des routeurs.')
            )
            return

        kpis = {kpi.name: kpi for kpi in KPI.objects.all()}
        
        # Créer des alertes de test avec différents niveaux de sévérité
        test_scenarios = [
            {
                'kpi_name': 'CPU',
                'value': 98,
                'severity': AlertSeverity.CRITICAL,
                'description': 'CPU critique sur routeur de test'
            },
            {
                'kpi_name': 'RAM',
                'value': 3500,
                'severity': AlertSeverity.HIGH,
                'description': 'Mémoire élevée sur routeur de test'
            },
            {
                'kpi_name': 'Traffic',
                'value': 150,
                'severity': AlertSeverity.MEDIUM,
                'description': 'Trafic modéré sur routeur de test'
            },
        ]

        for i, scenario in enumerate(test_scenarios):
            if scenario['kpi_name'] not in kpis:
                continue
                
            router = routers[i % len(routers)]
            kpi = kpis[scenario['kpi_name']]
            
            # Simuler un dépassement de seuil
            alert = AlertService.check_thresholds_and_create_alerts(
                router=router,
                interface=None,
                kpi=kpi,
                value=scenario['value'],
                timestamp=timezone.now()
            )
            
            if alert:
                self.stdout.write(
                    f'  ✓ Alerte de test créée: {alert.title} '
                    f'({alert.get_severity_display()})'
                )
            else:
                # Créer manuellement si le service n'a pas créé d'alerte
                from router_supervisor.alerts_app.models import Alert
                from decimal import Decimal
                
                alert = Alert.objects.create(
                    router=router,
                    kpi=kpi,
                    alert_type=AlertType.THRESHOLD,
                    severity=scenario['severity'],
                    title=f"Test: {scenario['description']}",
                    description=f"Alerte de test pour {kpi.name} sur {router.name}",
                    metric_name=kpi.name,
                    current_value=Decimal(str(scenario['value'])),
                    unit='%' if kpi.name == 'CPU' else ('MB' if kpi.name == 'RAM' else 'Mbps'),
                )
                self.stdout.write(
                    f'  ✓ Alerte de test créée manuellement: {alert.title}'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'  Alertes créées! Consultez le dashboard à /alerts/'
            )
        )
