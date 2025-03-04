from django.db import models

from django.core.validators import MinValueValidator

class Seuil(models.Model):
    ram = models.FloatField(
        validators=[MinValueValidator(0.1)],  # minimum 0.1
        verbose_name="RAM en Mo",
        default=300,
    )
    CPU = models.FloatField(
        validators=[MinValueValidator(1)],  # minimum 1
        verbose_name="CPU utilisé en %",
        default=50,
    )
    trafic = models.FloatField(
        validators=[MinValueValidator(0.001)],
        verbose_name="Bande passante en Mo/s",
        default=100,
    )
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du seuil",
        default="seuil",
    )

    def __str__(self):
        return f'{self.nom}'

class Routeur(models.Model):
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du routeur"
    )
    ip = models.GenericIPAddressField(
        protocol="IPv4",
        verbose_name="Adresse IP du routeur"
    )
    user = models.CharField(
        max_length=50,
        verbose_name="Nom d'utilisateur sur le routeur en ssh"
    )
    password = models.CharField(
        max_length=100,
        verbose_name="Mot de passe du routeur en ssh"
    )
    secret = models.CharField(
        max_length=100,
        verbose_name="Mot de passe pour enable"
    )
    seuil = models.ForeignKey(Seuil, on_delete=models.SET_DEFAULT, default=1) #ICI on configure la clé étrangère associée a Seuil, si Seuil est supprimé, seuil= Valueur-par-défaut

    def __str__(self):
        return f'{self.nom}'
