# Exemple dans un fichier de migration

from django.db import migrations


def create_default_threshold(apps, schema_editor):
    threshold = apps.get_model('config_routeur', 'threshold')  #
    threshold.objects.create(
        id=1,  # ID spécifique pour identifier cette instance
        ram=300,
        cpu=50,
        trafic=100,
        nom="threshold_par_defaut"
    )


def delete_default_threshold(apps, schema_editor):
    threshold = apps.get_model('config_routeur', 'threshold')
    threshold.objects.filter(id=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        # Ajoutez ici la migration précédente, par exemple :
        ('config_routeur', '0005_alter_threshold_nom'),
    ]

    operations = [
        migrations.RunPython(create_default_threshold, delete_default_threshold),
    ]
