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
    threshold = models.ForeignKey(
        Threshold, 
        on_delete=models.SET_DEFAULT, 
        default=1, 
        verbose_name="Associated threshold"
    )

    def __str__(self):
        return f'{self.name}'
