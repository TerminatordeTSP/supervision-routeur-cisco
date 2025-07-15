from django.contrib import admin
from .models import AlertRule, AlertInstance, AlertHistory


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric', 'condition', 'threshold_value', 'is_active', 'email_enabled')
    list_filter = ('metric', 'condition', 'is_active', 'email_enabled')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AlertInstance)
class AlertInstanceAdmin(admin.ModelAdmin):
    list_display = ('rule', 'router', 'severity', 'status', 'metric_value', 'triggered_at', 'email_sent')
    list_filter = ('severity', 'status', 'rule__metric', 'email_sent', 'triggered_at')
    search_fields = ('rule__name', 'router__name', 'message')
    readonly_fields = ('triggered_at', 'email_sent_at')
    actions = ['acknowledge_alerts', 'resolve_alerts']
    
    def acknowledge_alerts(self, request, queryset):
        count = queryset.filter(status='active').update(status='acknowledged', acknowledged_by=request.user)
        self.message_user(request, f'{count} alerts acknowledged.')
    acknowledge_alerts.short_description = "Acknowledge selected alerts"
    
    def resolve_alerts(self, request, queryset):
        count = queryset.exclude(status='resolved').update(status='resolved', resolved_by=request.user)
        self.message_user(request, f'{count} alerts resolved.')
    resolve_alerts.short_description = "Resolve selected alerts"


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = ('alert', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('alert__rule__name', 'changed_by__email')
    readonly_fields = ('changed_at',)
