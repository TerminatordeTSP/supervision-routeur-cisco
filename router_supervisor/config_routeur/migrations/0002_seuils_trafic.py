# Generated by Django 4.2.17 on 2025-01-01 22:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config_routeur', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thresholds',
            name='trafic',
            field=models.FloatField(default=0.001, validators=[django.core.validators.MinValueValidator(0.001)], verbose_name='Bande passante en Mo/s'),
            preserve_default=False,
        ),
    ]
