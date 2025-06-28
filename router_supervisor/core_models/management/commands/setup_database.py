from django.core.management.base import BaseCommand
from django.core.management import call_command
from core_models.models import (
    CustomUser, KPI, Seuil, Routeur, Interface, Alertes,
    UtilisateurRouteur, SeuilKPI
)
import os

class Command(BaseCommand):
    help = 'Initialize database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database before loading data',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Initializing Router Supervisor Database...")
        
        if options['reset']:
            self.stdout.write("⚠️  Resetting database...")
            call_command('flush', '--noinput')
        
        # Create superuser
        self.create_superuser()
        
        # Load initial data
        self.load_initial_data()
        
        self.stdout.write(
            self.style.SUCCESS("🎉 Database initialization completed successfully!")
        )

    def create_superuser(self):
        """Create superuser and sample users"""
        self.stdout.write("👤 Creating users...")
        
        if not CustomUser.objects.filter(is_superuser=True).exists():
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@telecom-sudparis.eu')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_user = os.environ.get('ADMIN_USER', 'admin')
            
            user = CustomUser.objects.create_superuser(
                username=admin_user,
                email=admin_email,
                password=admin_password,
                nom='Administrator',
                prenom='System',
                role='admin'
            )
            self.stdout.write(f"✅ Superuser '{admin_user}' created")
        
        # Create sample users
        if CustomUser.objects.count() <= 1:
            sample_users = [
                {
                    'username': 'operator1',
                    'email': 'operator1@telecom-sudparis.eu',
                    'password': 'operator123',
                    'nom': 'Dupont',
                    'prenom': 'Jean',
                    'role': 'user'
                },
                {
                    'username': 'viewer1',
                    'email': 'viewer1@telecom-sudparis.eu',
                    'password': 'viewer123',
                    'nom': 'Martin',
                    'prenom': 'Marie',
                    'role': 'viewer'
                }
            ]
            
            for user_data in sample_users:
                CustomUser.objects.create_user(**user_data)
            
            self.stdout.write(f"✅ Created {len(sample_users)} sample users")

    def load_initial_data(self):
        """Load initial data"""
        self.stdout.write("🌱 Loading initial data...")
        
        # Create KPIs
        if not KPI.objects.exists():
            kpis = [
                {'nom': 'CPU Usage'},
                {'nom': 'Memory Usage'},
                {'nom': 'Bandwidth Utilization'},
                {'nom': 'Packet Loss'},
                {'nom': 'Interface Status'},
                {'nom': 'Temperature'},
            ]
            
            for kpi_data in kpis:
                KPI.objects.create(**kpi_data)
            
            self.stdout.write(f"✅ Created {len(kpis)} KPIs")
        
        # Create Thresholds
        if not Seuil.objects.exists():
            seuils = [
                {
                    'id_seuil': 'STANDARD',
                    'nom': 'Standard Threshold',
                    'cpu': 80,
                    'ram': 85,
                    'trafic': 90,
                },
                {
                    'id_seuil': 'CRITICAL',
                    'nom': 'Critical Threshold',
                    'cpu': 95,
                    'ram': 95,
                    'trafic': 98,
                },
                {
                    'id_seuil': 'LOW',
                    'nom': 'Low Threshold',
                    'cpu': 60,
                    'ram': 70,
                    'trafic': 75,
                },
            ]
            
            for seuil_data in seuils:
                Seuil.objects.create(**seuil_data)
            
            self.stdout.write(f"✅ Created {len(seuils)} thresholds")
        
        # Create Routers
        if not Routeur.objects.exists():
            standard_seuil = Seuil.objects.get(id_seuil='STANDARD')
            critical_seuil = Seuil.objects.get(id_seuil='CRITICAL')
            
            routeurs = [
                {
                    'nom': 'Router-Core-01',
                    'ip': '192.168.1.1',
                    'username': 'admin',
                    'password': 'cisco123',
                    'secret': 'enable123',
                    'id_seuil': standard_seuil,
                },
                {
                    'nom': 'Router-Edge-01',
                    'ip': '192.168.1.2',
                    'username': 'admin',
                    'password': 'cisco123',
                    'secret': 'enable123',
                    'id_seuil': critical_seuil,
                },
                {
                    'nom': 'Router-Branch-01',
                    'ip': '192.168.1.10',
                    'username': 'admin',
                    'password': 'cisco123',
                    'secret': 'enable123',
                    'id_seuil': standard_seuil,
                },
            ]
            
            for routeur_data in routeurs:
                Routeur.objects.create(**routeur_data)
            
            self.stdout.write(f"✅ Created {len(routeurs)} routers")
        
        # Create Interfaces
        if not Interface.objects.exists():
            routeurs = Routeur.objects.all()
            interfaces_count = 0
            
            for routeur in routeurs:
                for i in range(3):
                    Interface.objects.create(
                        nom=f'GigabitEthernet0/0/{i}',
                        id_routeur=routeur,
                        trafic=0.0
                    )
                    interfaces_count += 1
            
            self.stdout.write(f"✅ Created {interfaces_count} interfaces")
        
        # Link KPIs to Thresholds
        if not SeuilKPI.objects.exists():
            seuils = Seuil.objects.all()
            kpis = KPI.objects.all()
            
            for seuil in seuils:
                for kpi in kpis:
                    if kpi.nom == 'CPU Usage':
                        valeur = seuil.cpu
                    elif kpi.nom == 'Memory Usage':
                        valeur = seuil.ram
                    elif kpi.nom == 'Bandwidth Utilization':
                        valeur = seuil.trafic
                    else:
                        valeur = 80.0
                    
                    SeuilKPI.objects.create(
                        seuil=seuil,
                        kpi=kpi,
                        valeur_seuil=valeur
                    )
            
            self.stdout.write("✅ Linked KPIs to thresholds")
        
        # Create sample user-router associations
        if not UtilisateurRouteur.objects.exists():
            try:
                operator = CustomUser.objects.get(username='operator1')
                viewer = CustomUser.objects.get(username='viewer1')
                routeurs = Routeur.objects.all()
                
                for routeur in routeurs:
                    UtilisateurRouteur.objects.create(
                        utilisateur=operator,
                        routeur=routeur,
                        access_level='write'
                    )
                    UtilisateurRouteur.objects.create(
                        utilisateur=viewer,
                        routeur=routeur,
                        access_level='read'
                    )
                
                self.stdout.write("✅ Created user-router associations")
            except CustomUser.DoesNotExist:
                self.stdout.write("⚠️  Sample users not found, skipping associations")
        
        self.stdout.write("🎉 Initial data loaded successfully!")
