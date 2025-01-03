from django.contrib import admin
from config_routeur.models import Seuil
from config_routeur.models import Routeur


class SeuilAdmin(admin.ModelAdmin):
    list_display = ('nom','ram', 'CPU', 'trafic') # liste les champs que nous voulons sur l'affichage de la liste sur le site admin
class RouteurAdmin(admin.ModelAdmin):
    list_display = ('nom','ip', 'user', 'password','secret','seuil')

admin.site.register(Seuil, SeuilAdmin)
admin.site.register(Routeur, RouteurAdmin)
"""
Cela signifie que dans l'interface Django Admin, une fois que le modèle **Seuil** est enregistrée avec cette classe `SeuilAdmin`, vous verrez une liste des instances du modèle **Seuil** où 
les colonnes affichées seront `ram`, `CPU` et `trafic` (des champs du modèle **Seuil**).
1. **Effet global :** En appelant `admin.site.register(Seuil, SeuilAdmin)`, vous indiquez à Django :
    - D'ajouter le modèle **Seuil** au site d'administration.
    - D'utiliser la configuration personnalisée définie dans la classe **SeuilAdmin** pour gérer l'affichage et d'autres options de ce modèle dans l'administration.
Résumé
En résumé, ce code permet de rendre le modèle **Seuil** gérable via le site Django Admin tout en appliquant une personnalisation (définie dans la classe **SeuilAdmin**) pour afficher 
les champs `ram`, `CPU` et `trafic` dans l'interface.
"""
