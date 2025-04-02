from django.db import models

from django.core.validators import MinValueValidator

class Threshold(models.Model):
    ram = models.FloatField(
        validators=[MinValueValidator(0.1)],  # minimum 0.1
        verbose_name="RAM in MB",
        default=300,
    )
    cpu = models.FloatField(
        validators=[MinValueValidator(1)],  # minimum 1
        verbose_name="CPU usage in %",
        default=50,
    )
    trafic = models.FloatField(
        validators=[MinValueValidator(0.001)],
        verbose_name="Bandwidth in MB/s",
        default=100,
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Threshold name",
        default="threshold",
    )

    def __str__(self):
        return f'{self.name}'



# ----------------------------
# Utilisateurs
# ----------------------------
class Utilisateur(models.Model):
    mail = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# ----------------------------
# Routeur
# ----------------------------
class Router(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Router name"
    )
    ip = models.GenericIPAddressField(
        protocol="IPv4",
        verbose_name="Router IP address"
    )
    user = models.CharField(
        max_length=50,
        verbose_name="SSH username for the router"
    )
    password = models.CharField(
        max_length=100,
        verbose_name="SSH password for the router"
    )
    secret = models.CharField(
        max_length=100,
        verbose_name="Enable password"
    )

    def __str__(self):
        return self.name

# ----------------------------
# Lien Utilisateur <-> Routeur (ManyToMany avec table personnalisée)
# ----------------------------
class UtilisateurRouteur(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    routeur = models.ForeignKey(Router, on_delete=models.CASCADE)

# ----------------------------
# Interface
# ----------------------------
class Interface(models.Model):
    interface_id = models.AutoField(primary_key=True)
    trafic = models.FloatField()
    routeur = models.ForeignKey(Router, on_delete=models.CASCADE, related_name="interfaces")

    def __str__(self):
        return f"Interface {self.interface_id} - {self.trafic} Mbps"

# ----------------------------
# Seuil
# ----------------------------
class Seuil(models.Model):
    ram = models.FloatField()
    cpu = models.FloatField()
    trafic = models.FloatField()
    nom = models.CharField(max_length=100)
    routeur = models.OneToOneField(Router, on_delete=models.CASCADE, related_name="seuil")

    def __str__(self):
        return self.nom

# ----------------------------
# KPI
# ----------------------------
class KPI(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# ----------------------------
# Seuil <-> KPI (ManyToMany)
# ----------------------------
class SeuilKPI(models.Model):
    seuil = models.ForeignKey(Seuil, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

# ----------------------------
# Alertes
# ----------------------------
class Alerte(models.Model):
    date_log = models.DateTimeField()
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alerte {self.id} - {self.date_log}"