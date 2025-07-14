from django.db import models
from django.utils import timezone
from router_supervisor.core_models.models import Router, Interface, Threshold, KPI


class AlertSeverity(models.TextChoices):
    LOW = 'LOW', 'Faible'
    MEDIUM = 'MEDIUM', 'Moyen'
    HIGH = 'HIGH', 'Élevé'
    CRITICAL = 'CRITICAL', 'Critique'


class AlertStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acquittée'
    RESOLVED = 'RESOLVED', 'Résolue'
    DISMISSED = 'DISMISSED', 'Ignorée'


class AlertType(models.TextChoices):
    THRESHOLD = 'THRESHOLD', 'Dépassement de seuil'
    INTERFACE_DOWN = 'INTERFACE_DOWN', 'Interface hors service'
    HIGH_ERROR_RATE = 'HIGH_ERROR_RATE', 'Taux d\'erreur élevé'
    CONNECTIVITY = 'CONNECTIVITY', 'Problème de connectivité'


class Alert(models.Model):
    """
    Modèle d'alerte pour enregistrer les alertes générées lors du dépassement de seuils
    """
    alert_id = models.AutoField(primary_key=True)
    
    # Relations
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='alerts')
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    threshold = models.ForeignKey(Threshold, on_delete=models.SET_NULL, null=True, blank=True)
    kpi = models.ForeignKey(KPI, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Détails de l'alerte
    alert_type = models.CharField(max_length=20, choices=AlertType.choices, default=AlertType.THRESHOLD)
    severity = models.CharField(max_length=10, choices=AlertSeverity.choices, default=AlertSeverity.MEDIUM)
    status = models.CharField(max_length=15, choices=AlertStatus.choices, default=AlertStatus.ACTIVE)
    
    # Messages et valeurs
    title = models.CharField(max_length=200)
    description = models.TextField()
    metric_name = models.CharField(max_length=50)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, default='')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    log_id = models.IntegerField(null=True, blank=True)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        app_label = 'alerts_app'
        db_table = 'alerts_alert'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['router', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['alert_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.router.name} ({self.get_severity_display()})"
    
    def acknowledge(self, user=None):
        """Marquer l'alerte comme acquittée"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, user=None):
        """Marquer l'alerte comme résolue"""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = timezone.now()
        self.save()
    
    def dismiss(self, user=None):
        """Ignorer l'alerte"""
        self.status = AlertStatus.DISMISSED
        self.save()
    
    @property
    def is_active(self):
        return self.status == AlertStatus.ACTIVE
    
    @property
    def duration(self):
        """Durée depuis la création de l'alerte"""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return timezone.now() - self.created_at
    
    @classmethod
    def get_active_alerts_count(cls):
        """Nombre d'alertes actives"""
        return cls.objects.filter(status=AlertStatus.ACTIVE).count()
    
    @classmethod
    def get_critical_alerts_count(cls):
        """Nombre d'alertes critiques actives"""
        return cls.objects.filter(
            status=AlertStatus.ACTIVE,
            severity=AlertSeverity.CRITICAL
        ).count()


class AlertHistory(models.Model):
    """
    Historique des changements d'état des alertes
    """
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=15, choices=AlertStatus.choices)
    new_status = models.CharField(max_length=15, choices=AlertStatus.choices)
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.CharField(max_length=100, null=True, blank=True)  # User email or system
    comment = models.TextField(blank=True)
    
    class Meta:
        app_label = 'alerts_app'
        db_table = 'alerts_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"Alert {self.alert.alert_id}: {self.previous_status} → {self.new_status}"


class AlertRule(models.Model):
    """
    Règles personnalisées pour la génération d'alertes
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Conditions
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    operator = models.CharField(max_length=10, choices=[
        ('gt', 'Supérieur à'),
        ('gte', 'Supérieur ou égal à'),
        ('lt', 'Inférieur à'),
        ('lte', 'Inférieur ou égal à'),
        ('eq', 'Égal à'),
        ('ne', 'Différent de'),
    ])
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Configuration de l'alerte
    severity = models.CharField(max_length=10, choices=AlertSeverity.choices)
    alert_type = models.CharField(max_length=20, choices=AlertType.choices, default=AlertType.THRESHOLD)
    
    # Filtres optionnels
    router = models.ForeignKey(Router, on_delete=models.CASCADE, null=True, blank=True, 
                              help_text="Si spécifié, la règle ne s'applique qu'à ce routeur")
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, null=True, blank=True,
                                 help_text="Si spécifié, la règle ne s'applique qu'à cette interface")
    
    # Paramètres
    is_active = models.BooleanField(default=True)
    cooldown_minutes = models.IntegerField(default=5, 
                                          help_text="Délai minimum entre deux alertes pour la même règle")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'alerts_app'
        db_table = 'alerts_rule'
        unique_together = [['name', 'kpi', 'router', 'interface']]
    
    def __str__(self):
        return f"{self.name} ({self.kpi.name} {self.operator} {self.threshold_value})"
    
    def check_condition(self, value):
        """Vérifier si la valeur déclenche la règle"""
        if self.operator == 'gt':
            return value > self.threshold_value
        elif self.operator == 'gte':
            return value >= self.threshold_value
        elif self.operator == 'lt':
            return value < self.threshold_value
        elif self.operator == 'lte':
            return value <= self.threshold_value
        elif self.operator == 'eq':
            return value == self.threshold_value
        elif self.operator == 'ne':
            return value != self.threshold_value
        return False
    
    def should_trigger_alert(self, router, interface=None):
        """Vérifier si une alerte peut être déclenchée (cooldown)"""
        if not self.is_active:
            return False
        
        # Vérifier le cooldown
        cooldown_time = timezone.now() - timezone.timedelta(minutes=self.cooldown_minutes)
        recent_alerts = Alert.objects.filter(
            router=router,
            kpi=self.kpi,
            created_at__gte=cooldown_time
        )
        
        if interface:
            recent_alerts = recent_alerts.filter(interface=interface)
        
        return not recent_alerts.exists()
