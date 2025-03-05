# Exemple dans un fichier de migration

from django.db import migrations


def create_default_seuil(apps, schema_editor):
    Seuil = apps.get_model('config_routeur', 'Seuil')  #
    Seuil.objects.create(
        id=1,  # ID spécifique pour identifier cette instance
        ram=300,
        CPU=50,
        trafic=100,
        nom="seuil_par_defaut"
    )


def delete_default_seuil(apps, schema_editor):
    Seuil = apps.get_model('config_routeur', 'Seuil')
    Seuil.objects.filter(id=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        # Ajoutez ici la migration précédente, par exemple :
        ('config_routeur', '0005_alter_seuil_nom'),
    ]

    operations = [
        migrations.RunPython(create_default_seuil, delete_default_seuil),
    ]
