from django.contrib import admin
from router_supervisor.core_models.models import (
    User,
    Threshold,
    KPI,
    Router,
    Interface,
    Alert,
    User_Router,
    Router_Interface_Log,
    Threshold_KPI,
    KPI_Interface_Log
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'first_name', 'last_name', 'role')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(Threshold)
class ThresholdAdmin(admin.ModelAdmin):
    list_display = ('threshold_id', 'name', 'ram', 'cpu', 'traffic')
    search_fields = ('name',)

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('kpi_id', 'name')
    search_fields = ('name',)

@admin.register(Router)
class RouterAdmin(admin.ModelAdmin):
    list_display = ('router_id', 'name', 'ip_address', 'username')
    search_fields = ('name', 'ip_address')

@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('interface_id', 'router', 'traffic')
    search_fields = ('router__name',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('interface', 'log_id', 'log_date')
    search_fields = ('interface__router__name',)

@admin.register(User_Router)
class UserRouterAdmin(admin.ModelAdmin):
    list_display = ('user', 'router')
    search_fields = ('user__email', 'router__name')

@admin.register(Router_Interface_Log)
class RouterInterfaceLogAdmin(admin.ModelAdmin):
    list_display = ('router', 'interface', 'log_id')
    search_fields = ('router__name', 'interface__router__name')

@admin.register(Threshold_KPI)
class ThresholdKPIAdmin(admin.ModelAdmin):
    list_display = ('threshold', 'kpi')
    search_fields = ('threshold__name', 'kpi__name')

@admin.register(KPI_Interface_Log)
class KPIInterfaceLogAdmin(admin.ModelAdmin):
    list_display = ('interface', 'log_id', 'kpi')
    search_fields = ('interface__router__name', 'kpi__name')