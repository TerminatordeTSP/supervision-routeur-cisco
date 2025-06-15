from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.AddField(
            model_name='interface',
            name='name',
            field=models.CharField(default='default', max_length=100),
        ),
        migrations.AddField(
            model_name='interface',
            name='status',
            field=models.CharField(default='unknown', max_length=20),
        ),
        migrations.AddField(
            model_name='interface',
            name='input_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AddField(
            model_name='interface',
            name='output_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AddField(
            model_name='interface',
            name='errors',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interface',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='kpi_interface_log',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AddField(
            model_name='kpi_interface_log',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='interface',
            unique_together={('router', 'name')},
        ),
        migrations.AddIndex(
            model_name='kpi_interface_log',
            index=models.Index(fields=['timestamp'], name='kpi_interfa_timesta_c6b50c_idx'),
        ),
        migrations.AddIndex(
            model_name='kpi_interface_log',
            index=models.Index(fields=['interface', 'kpi'], name='kpi_interfa_interfa_c1c9d5_idx'),
        ),
    ]