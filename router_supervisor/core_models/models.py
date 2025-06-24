from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Extended User model based on your Utilisateurs table"""
    nom = models.CharField(max_length=50, blank=True)
    prenom = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, default='user', choices=[
        ('admin', 'Administrator'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    ])
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.username})"

class KPI(models.Model):
    """KPI model"""
    kpi_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"
    
    def __str__(self):
        return self.nom

class Seuil(models.Model):
    """Threshold model"""
    id_seuil = models.CharField(max_length=50, primary_key=True)
    ram = models.IntegerField(help_text="RAM threshold in %")
    cpu = models.IntegerField(help_text="CPU threshold in %")
    trafic = models.IntegerField(help_text="Traffic threshold in %")
    nom = models.CharField(max_length=50)
    kpis = models.ManyToManyField(KPI, through='SeuilKPI', blank=True)
    
    class Meta:
        verbose_name = "Seuil"
        verbose_name_plural = "Seuils"
    
    def __str__(self):
        return f"{self.nom} (CPU:{self.cpu}%, RAM:{self.ram}%, Traffic:{self.trafic}%)"

class Routeur(models.Model):
    """Router model"""
    id_routeur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    secret = models.CharField(max_length=50, blank=True)
    id_seuil = models.ForeignKey(Seuil, on_delete=models.CASCADE)
    utilisateurs = models.ManyToManyField(CustomUser, through='UtilisateurRouteur', blank=True)
    
    class Meta:
        verbose_name = "Routeur"
        verbose_name_plural = "Routeurs"
    
    def __str__(self):
        return f"{self.nom} ({self.ip})"

class Interface(models.Model):
    """Interface model"""
    interface_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, blank=True)
    trafic = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    id_routeur = models.ForeignKey(Routeur, on_delete=models.CASCADE, related_name='interfaces')
    
    class Meta:
        verbose_name = "Interface"
        verbose_name_plural = "Interfaces"
    
    def __str__(self):
        return f"{self.nom or f'Interface {self.interface_id}'} on {self.id_routeur.nom}"

class Alertes(models.Model):
    """Alerts model"""
    id_log = models.AutoField(primary_key=True)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='alertes')
    date_log = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    resolved = models.BooleanField(default=False)
    kpis = models.ManyToManyField(KPI, through='KPIInterfaceLog', blank=True)
    
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-date_log']
    
    def __str__(self):
        return f"Alert {self.id_log} - {self.interface} at {self.date_log}"

# Through models for many-to-many relationships

class UtilisateurRouteur(models.Model):
    """User-Router relationship"""
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    routeur = models.ForeignKey(Routeur, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=20, choices=[
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
        ('admin', 'Admin'),
    ], default='read')
    
    class Meta:
        unique_together = ('utilisateur', 'routeur')
        verbose_name = "Utilisateur Routeur"
        verbose_name_plural = "Utilisateurs Routeurs"
    
    def __str__(self):
        return f"{self.utilisateur} -> {self.routeur} ({self.access_level})"

class SeuilKPI(models.Model):
    """Threshold-KPI relationship"""
    seuil = models.ForeignKey(Seuil, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    valeur_seuil = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ('seuil', 'kpi')
        verbose_name = "Seuil KPI"
        verbose_name_plural = "Seuils KPI"
    
    def __str__(self):
        return f"{self.seuil.nom} - {self.kpi.nom}: {self.valeur_seuil}"

class KPIInterfaceLog(models.Model):
    """KPI-Interface-Log relationship"""
    alerte = models.ForeignKey(Alertes, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    valeur = models.FloatField()
    
    class Meta:
        unique_together = ('alerte', 'kpi')
        verbose_name = "KPI Interface Log"
        verbose_name_plural = "KPI Interface Logs"
    
    def __str__(self):
        return f"{self.kpi.nom}: {self.valeur} (Alert {self.alerte.id_log})"
