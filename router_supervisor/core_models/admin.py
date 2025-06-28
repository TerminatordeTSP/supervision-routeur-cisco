from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, KPI, Seuil, Routeur, Interface, Alertes,
    UtilisateurRouteur, SeuilKPI, KPIInterfaceLog
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin for Custom User model"""
    list_display = ('username', 'email', 'nom', 'prenom', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'nom', 'prenom')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('nom', 'prenom', 'role')
        }),
    )

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    """Admin for KPI model"""
    list_display = ('kpi_id', 'nom')
    search_fields = ('nom',)
    ordering = ('nom',)

@admin.register(Seuil)
class SeuilAdmin(admin.ModelAdmin):
    """Admin for Seuil model"""
    list_display = ('id_seuil', 'nom', 'cpu', 'ram', 'trafic')
    list_filter = ('cpu', 'ram', 'trafic')
    search_fields = ('id_seuil', 'nom')
    filter_horizontal = ('kpis',)

@admin.register(Routeur)
class RouteurAdmin(admin.ModelAdmin):
    """Admin for Routeur model"""
    list_display = ('id_routeur', 'nom', 'ip', 'username', 'id_seuil')
    list_filter = ('id_seuil',)
    search_fields = ('nom', 'ip', 'username')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'ip', 'id_seuil')
        }),
        ('Connexion', {
            'fields': ('username', 'password', 'secret'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    """Admin for Interface model"""
    list_display = ('interface_id', 'nom', 'id_routeur', 'trafic')
    list_filter = ('id_routeur',)
    search_fields = ('nom', 'id_routeur__nom', 'id_routeur__ip')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('id_routeur')

@admin.register(Alertes)
class AlertesAdmin(admin.ModelAdmin):
    """Admin for Alertes model"""
    list_display = ('id_log', 'interface', 'date_log', 'severity', 'resolved')
    list_filter = ('severity', 'resolved', 'date_log')
    search_fields = ('interface__nom', 'interface__id_routeur__nom', 'message')
    readonly_fields = ('date_log',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('interface', 'date_log', 'severity', 'resolved')
        }),
        ('Détails', {
            'fields': ('message',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('interface__id_routeur')

@admin.register(UtilisateurRouteur)
class UtilisateurRouteurAdmin(admin.ModelAdmin):
    """Admin for UtilisateurRouteur model"""
    list_display = ('utilisateur', 'routeur', 'access_level')
    list_filter = ('access_level',)
    search_fields = ('utilisateur__username', 'routeur__nom')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('utilisateur', 'routeur')

@admin.register(SeuilKPI)
class SeuilKPIAdmin(admin.ModelAdmin):
    """Admin for SeuilKPI model"""
    list_display = ('seuil', 'kpi', 'valeur_seuil')
    list_filter = ('seuil', 'kpi')
    search_fields = ('seuil__nom', 'kpi__nom')

@admin.register(KPIInterfaceLog)
class KPIInterfaceLogAdmin(admin.ModelAdmin):
    """Admin for KPIInterfaceLog model"""
    list_display = ('alerte', 'kpi', 'valeur')
    list_filter = ('kpi', 'alerte__severity')
    search_fields = ('kpi__nom', 'alerte__interface__nom')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('alerte', 'kpi')
