from django.db import models
from django.contrib.auth import get_user_model
from router_supervisor.core_models.models import Router, Threshold, Alert as CoreAlert


User = get_user_model()


class AlertRule(models.Model):
    """Rules that define when alerts should be triggered"""
    METRIC_CHOICES = [
        ('cpu', 'CPU Usage'),
        ('ram', 'RAM Usage'),
        ('traffic', 'Traffic'),
    ]
    
    CONDITION_CHOICES = [
        ('gt', 'Greater than'),
        ('gte', 'Greater than or equal'),
        ('lt', 'Less than'),
        ('lte', 'Less than or equal'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    metric = models.CharField(max_length=20, choices=METRIC_CHOICES)
    condition = models.CharField(max_length=3, choices=CONDITION_CHOICES, default='gt')
    threshold_value = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email settings
    email_enabled = models.BooleanField(default=True)
    email_recipients = models.TextField(
        help_text="Email addresses separated by commas",
        blank=True
    )
    
    def __str__(self):
        return f"{self.name} ({self.metric} {self.condition} {self.threshold_value})"
    
    class Meta:
        db_table = 'alert_rule'


class AlertInstance(models.Model):
    """Individual alert instances triggered by rules"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alert_instances')
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='alert_instances')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    
    # Alert details
    message = models.TextField()
    metric_value = models.FloatField()
    threshold_value = models.FloatField()
    
    # Timestamps
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Email tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # User who acknowledged/resolved
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alert_instances'
    )
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_alert_instances'
    )
    
    def __str__(self):
        return f"Alert: {self.rule.name} for {self.router.name} at {self.triggered_at}"
    
    class Meta:
        db_table = 'alert_instance'
        ordering = ['-triggered_at']


class AlertHistory(models.Model):
    """History of alert state changes"""
    alert = models.ForeignKey(AlertInstance, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=12, choices=AlertInstance.STATUS_CHOICES)
    new_status = models.CharField(max_length=12, choices=AlertInstance.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.alert.rule.name}: {self.old_status} → {self.new_status}"
    
    class Meta:
        db_table = 'alert_history'
        ordering = ['-changed_at']
