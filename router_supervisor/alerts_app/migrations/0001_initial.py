# Generated migration for alerts_app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core_models', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('metric', models.CharField(choices=[('cpu', 'CPU Usage'), ('ram', 'RAM Usage'), ('traffic', 'Traffic')], max_length=20)),
                ('condition', models.CharField(choices=[('gt', 'Greater than'), ('gte', 'Greater than or equal'), ('lt', 'Less than'), ('lte', 'Less than or equal')], default='gt', max_length=3)),
                ('threshold_value', models.FloatField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email_enabled', models.BooleanField(default=True)),
                ('email_recipients', models.TextField(blank=True, help_text='Email addresses separated by commas')),
            ],
            options={
                'db_table': 'alert_rule',
            },
        ),
        migrations.CreateModel(
            name='AlertHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(max_length=12)),
                ('new_status', models.CharField(max_length=12)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(blank=True)),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'alert_history',
                'ordering': ['-changed_at'],
            },
        ),
        migrations.CreateModel(
            name='AlertInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('active', 'Active'), ('acknowledged', 'Acknowledged'), ('resolved', 'Resolved')], default='active', max_length=12)),
                ('message', models.TextField()),
                ('metric_value', models.FloatField()),
                ('threshold_value', models.FloatField()),
                ('triggered_at', models.DateTimeField(auto_now_add=True)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_sent_at', models.DateTimeField(blank=True, null=True)),
                ('acknowledged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acknowledged_alert_instances', to=settings.AUTH_USER_MODEL)),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_alert_instances', to=settings.AUTH_USER_MODEL)),
                ('router', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alert_instances', to='core_models.router')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alert_instances', to='alerts_app.alertrule')),
            ],
            options={
                'db_table': 'alert_instance',
                'ordering': ['-triggered_at'],
            },
        ),
        migrations.AddField(
            model_name='alerthistory',
            name='alert',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='alerts_app.alertinstance'),
        ),
    ]
