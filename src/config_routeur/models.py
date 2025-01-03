from django.db import models

from django.core.validators import MinValueValidator

class Seuil(models.Model):
    ram = models.FloatField(
        validators=[MinValueValidator(0.1)],  # minimum 0.1
        verbose_name="RAM en Mo",
    )
    CPU = models.FloatField(
        validators=[MinValueValidator(1)],  # minimum 1
        verbose_name="CPU utilisé en %",
    )
    trafic = models.FloatField(
        validators=[MinValueValidator(0.001)],
        verbose_name="Bande passante en Mo/s",
    )
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du seuil"
    )



