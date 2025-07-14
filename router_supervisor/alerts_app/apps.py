from django.apps import AppConfig


class AlertsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alerts_app'
    verbose_name = 'Système d\'Alertes'
    
    def ready(self):
        """Initialisation des services d'alertes"""
        pass
