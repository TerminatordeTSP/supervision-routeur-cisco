from django.contrib import admin
from thresholds_app.models import Threshold
from thresholds_app.models import Router


class ThresholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'ram', 'cpu', 'trafic')
class RouterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'user', 'password', 'secret', 'threshold')

admin.site.register(Threshold, ThresholdAdmin)
admin.site.register(Router, RouterAdmin)