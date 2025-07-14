from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Alert, AlertRule, AlertHistory


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'alert_id', 'title', 'router', 'interface', 'severity_badge',
        'status_badge', 'alert_type', 'created_at', 'actions'
    ]
    list_filter = [
        'status', 'severity', 'alert_type', 'created_at',
        'router', 'kpi'
    ]
    search_fields = [
        'title', 'description', 'router__name', 'interface__name',
        'metric_name'
    ]
    readonly_fields = [
        'alert_id', 'created_at', 'updated_at', 'duration_display'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Informations principales', {
            'fields': [
                'alert_id', 'title', 'description', 'alert_type', 
                'severity', 'status'
            ]
        }),
        ('Relations', {
            'fields': [
                'router', 'interface', 'threshold', 'kpi'
            ]
        }),
        ('Métriques', {
            'fields': [
                'metric_name', 'current_value', 'threshold_value', 'unit'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at', 'updated_at', 'acknowledged_at', 
                'resolved_at', 'duration_display'
            ]
        }),
        ('Données supplémentaires', {
            'fields': ['log_id', 'additional_data'],
            'classes': ['collapse']
        })
    ]
    
    def severity_badge(self, obj):
        color_map = {
            'LOW': '#28a745',      # Vert
            'MEDIUM': '#ffc107',   # Jaune
            'HIGH': '#fd7e14',     # Orange
            'CRITICAL': '#dc3545' # Rouge
        }
        color = color_map.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Sévérité'
    
    def status_badge(self, obj):
        color_map = {
            'ACTIVE': '#dc3545',        # Rouge
            'ACKNOWLEDGED': '#ffc107',  # Jaune
            'RESOLVED': '#28a745',      # Vert
            'DISMISSED': '#6c757d'      # Gris
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def duration_display(self, obj):
        if obj.resolved_at:
            duration = obj.resolved_at - obj.created_at
        else:
            duration = timezone.now() - obj.created_at
        
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    duration_display.short_description = 'Durée'
    
    def actions(self, obj):
        buttons = []
        
        if obj.status == 'ACTIVE':
            buttons.append(
                f'<a href="#" onclick="acknowledgeAlert({obj.alert_id})" '
                f'style="color: #ffc107; margin-right: 10px;">Acquitter</a>'
            )
            buttons.append(
                f'<a href="#" onclick="resolveAlert({obj.alert_id})" '
                f'style="color: #28a745;">Résoudre</a>'
            )
        
        return mark_safe(' | '.join(buttons)) if buttons else '-'
    actions.short_description = 'Actions'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'router', 'interface', 'threshold', 'kpi'
        )
    
    class Media:
        js = ['admin/js/alert_actions.js']


class AlertHistoryInline(admin.TabularInline):
    model = AlertHistory
    extra = 0
    readonly_fields = ['changed_at']
    ordering = ['-changed_at']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'kpi', 'operator', 'threshold_value', 'severity_badge',
        'router', 'interface', 'is_active_badge', 'created_at'
    ]
    list_filter = [
        'is_active', 'severity', 'alert_type', 'operator', 
        'kpi', 'router', 'created_at'
    ]
    search_fields = ['name', 'description', 'kpi__name', 'router__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Informations générales', {
            'fields': ['name', 'description', 'is_active']
        }),
        ('Conditions', {
            'fields': [
                'kpi', 'operator', 'threshold_value'
            ]
        }),
        ('Configuration de l\'alerte', {
            'fields': ['severity', 'alert_type']
        }),
        ('Filtres (optionnels)', {
            'fields': ['router', 'interface'],
            'description': 'Laissez vide pour appliquer la règle à tous les routeurs/interfaces'
        }),
        ('Paramètres', {
            'fields': ['cooldown_minutes']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def severity_badge(self, obj):
        color_map = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
        color = color_map.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Sévérité'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Inactive</span>'
            )
    is_active_badge.short_description = 'État'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'kpi', 'router', 'interface'
        )


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'alert', 'previous_status', 'new_status', 'changed_by', 'changed_at'
    ]
    list_filter = ['previous_status', 'new_status', 'changed_at']
    search_fields = ['alert__title', 'changed_by', 'comment']
    readonly_fields = ['changed_at']
    ordering = ['-changed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('alert')


# Actions personnalisées pour les alertes
@admin.action(description='Acquitter les alertes sélectionnées')
def acknowledge_selected_alerts(modeladmin, request, queryset):
    updated = 0
    for alert in queryset.filter(status='ACTIVE'):
        alert.acknowledge()
        updated += 1
    
    modeladmin.message_user(
        request,
        f'{updated} alerte(s) acquittée(s) avec succès.'
    )


@admin.action(description='Résoudre les alertes sélectionnées')
def resolve_selected_alerts(modeladmin, request, queryset):
    updated = 0
    for alert in queryset.filter(status__in=['ACTIVE', 'ACKNOWLEDGED']):
        alert.resolve()
        updated += 1
    
    modeladmin.message_user(
        request,
        f'{updated} alerte(s) résolue(s) avec succès.'
    )


# Ajouter les actions à l'admin des alertes
AlertAdmin.actions = [acknowledge_selected_alerts, resolve_selected_alerts]
