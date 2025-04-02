from django.contrib import admin
from thresholds_app.models import Threshold, Router

class ThresholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'ram', 'cpu', 'trafic')

class RouterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'user', 'password', 'secret', 'get_threshold_name')

    def get_threshold_name(self, obj):
        # Accède au seuil via le related_name du OneToOneField
        return obj.seuil.name if hasattr(obj, 'seuil') else 'Aucun seuil'

    get_threshold_name.short_description = 'Seuil associé'

admin.site.register(Threshold, ThresholdAdmin)
admin.site.register(Router, RouterAdmin)