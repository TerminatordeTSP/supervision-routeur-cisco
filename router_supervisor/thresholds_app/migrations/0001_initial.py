# Generated by Django 4.2.17 on 2025-06-27 23:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KPI',
            fields=[
                ('kpi_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'kpi',
            },
        ),
        migrations.CreateModel(
            name='Threshold',
            fields=[
                ('threshold_id', models.AutoField(primary_key=True, serialize=False)),
                ('ram', models.IntegerField()),
                ('cpu', models.IntegerField()),
                ('traffic', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'threshold',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=50)),
                ('role', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='Router',
            fields=[
                ('router_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('ip_address', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('secret', models.CharField(max_length=50)),
                ('threshold', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.threshold')),
            ],
            options={
                'db_table': 'router',
            },
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('interface_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='default', max_length=100)),
                ('traffic', models.DecimalField(decimal_places=2, max_digits=15)),
                ('status', models.CharField(default='unknown', max_length=20)),
                ('input_rate', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('output_rate', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('errors', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('router', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.router')),
            ],
            options={
                'db_table': 'interface',
                'unique_together': {('router', 'name')},
            },
        ),
        migrations.CreateModel(
            name='User_Router',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('router', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.router')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.user')),
            ],
            options={
                'db_table': 'user_router',
                'unique_together': {('user', 'router')},
            },
        ),
        migrations.CreateModel(
            name='Threshold_KPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kpi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.kpi')),
                ('threshold', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.threshold')),
            ],
            options={
                'db_table': 'threshold_kpi',
                'unique_together': {('threshold', 'kpi')},
            },
        ),
        migrations.CreateModel(
            name='Router_Interface_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_id', models.IntegerField()),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.interface')),
                ('router', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.router')),
            ],
            options={
                'db_table': 'router_interface_log',
                'unique_together': {('router', 'interface', 'log_id')},
            },
        ),
        migrations.CreateModel(
            name='KPI_Interface_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_id', models.IntegerField()),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.interface')),
                ('kpi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.kpi')),
            ],
            options={
                'db_table': 'kpi_interface_log',
                'indexes': [models.Index(fields=['timestamp'], name='kpi_interfa_timesta_f72566_idx'), models.Index(fields=['interface', 'kpi'], name='kpi_interfa_interfa_4f58d6_idx')],
                'unique_together': {('interface', 'log_id', 'kpi')},
            },
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_id', models.IntegerField()),
                ('log_date', models.DateTimeField()),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thresholds_app.interface')),
            ],
            options={
                'db_table': 'alert',
                'unique_together': {('interface', 'log_id')},
            },
        ),
    ]
