# Generated by Django 4.2.17 on 2025-06-28 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('thresholds_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('orange', 'Orange Theme'), ('blue', 'Blue Theme'), ('green', 'Green Theme')], default='orange', max_length=20)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'Français'), ('es', 'Español')], default='en', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='thresholds_app.user')),
            ],
            options={
                'db_table': 'user_preferences',
            },
        ),
    ]
