# Generated by Django 4.2.17 on 2025-01-01 22:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config_routeur', '0002_thresholds_trafic'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='thresholds',
            new_name='threshold',
        ),
    ]
