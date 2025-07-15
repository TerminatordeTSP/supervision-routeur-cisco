from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import AlertInstance, AlertRule, AlertHistory
from .forms import AlertRuleForm, AlertAcknowledgeForm, AlertResolveForm
from .utils import acknowledge_alert, resolve_alert, send_alert_email
import json


@login_required
def alerts_index(request):
    """Main alerts dashboard"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    severity_filter = request.GET.get('severity', 'all')
    search = request.GET.get('search', '')
    
    # Base queryset
    alerts = AlertInstance.objects.select_related('rule', 'router', 'acknowledged_by', 'resolved_by')
    
    # Apply filters
    if status_filter != 'all':
        alerts = alerts.filter(status=status_filter)
    
    if severity_filter != 'all':
        alerts = alerts.filter(severity=severity_filter)
    
    if search:
        alerts = alerts.filter(
            Q(rule__name__icontains=search) |
            Q(router__name__icontains=search) |
            Q(message__icontains=search)
        )
    
    # Get statistics
    stats = {
        'total': AlertInstance.objects.count(),
        'active': AlertInstance.objects.filter(status='active').count(),
        'acknowledged': AlertInstance.objects.filter(status='acknowledged').count(),
        'resolved': AlertInstance.objects.filter(status='resolved').count(),
        'critical': AlertInstance.objects.filter(severity='critical', status='active').count(),
    }
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'search': search,
    }
    
    return render(request, 'alerts_app/alerts_index.html', context)


@login_required
def alert_detail(request, alert_id):
    """Alert detail view"""
    alert = get_object_or_404(AlertInstance, id=alert_id)
    history = alert.history.all().order_by('-changed_at')
    
    context = {
        'alert': alert,
        'history': history,
    }
    
    return render(request, 'alerts_app/alert_detail.html', context)


@login_required
def alert_acknowledge(request, alert_id):
    """Acknowledge an alert"""
    alert = get_object_or_404(AlertInstance, id=alert_id)
    
    if request.method == 'POST':
        form = AlertAcknowledgeForm(request.POST)
        if form.is_valid():
            if acknowledge_alert(alert, request.user, form.cleaned_data.get('comment', '')):
                messages.success(request, 'Alert acknowledged successfully.')
                return redirect('alerts:alert_detail', alert_id=alert.id)
            else:
                messages.error(request, 'Failed to acknowledge alert.')
    else:
        form = AlertAcknowledgeForm()
    
    context = {
        'alert': alert,
        'form': form,
        'action': 'acknowledge'
    }
    
    return render(request, 'alerts_app/alert_action.html', context)


@login_required
def alert_resolve(request, alert_id):
    """Resolve an alert"""
    alert = get_object_or_404(AlertInstance, id=alert_id)
    
    if request.method == 'POST':
        form = AlertResolveForm(request.POST)
        if form.is_valid():
            if resolve_alert(alert, request.user, form.cleaned_data.get('comment', '')):
                messages.success(request, 'Alert resolved successfully.')
                return redirect('alerts:alert_detail', alert_id=alert.id)
            else:
                messages.error(request, 'Failed to resolve alert.')
    else:
        form = AlertResolveForm()
    
    context = {
        'alert': alert,
        'form': form,
        'action': 'resolve'
    }
    
    return render(request, 'alerts_app/alert_action.html', context)


@login_required
def rules_index(request):
    """Alert rules management"""
    rules = AlertRule.objects.all().order_by('-created_at')
    
    # Get rule statistics
    for rule in rules:
        rule.alert_count = rule.alert_instances.count()
        rule.active_alerts = rule.alert_instances.filter(status='active').count()
    
    context = {
        'rules': rules,
    }
    
    return render(request, 'alerts_app/rules_index.html', context)


@login_required
def rule_detail(request, rule_id):
    """View details of an alert rule (read-only)"""
    rule = get_object_or_404(AlertRule, id=rule_id)
    
    # Get rule statistics
    rule.alert_count = rule.alert_instances.count()
    rule.active_alerts = rule.alert_instances.filter(status='active').count()
    rule.recent_alerts = rule.alert_instances.order_by('-triggered_at')[:10]
    
    context = {
        'rule': rule,
    }
    
    return render(request, 'alerts_app/rule_detail.html', context)


@login_required
def sync_rules_from_thresholds(request):
    """Synchronize alert rules from existing thresholds"""
    if request.method == 'POST':
        from django.core.management import call_command
        from io import StringIO
        
        # Capture the command output
        output = StringIO()
        try:
            call_command('sync_threshold_rules', stdout=output)
            messages.success(request, 'Alert rules synchronized successfully with thresholds.')
            
            # Show detailed output in debug mode
            if hasattr(request, 'user') and request.user.is_superuser:
                output_content = output.getvalue()
                if output_content:
                    messages.info(request, f"Sync details: {output_content}")
                    
        except Exception as e:
            messages.error(request, f'Failed to sync rules: {str(e)}')
        
        return redirect('alerts:rules_index')
    
    # Show confirmation page
    from router_supervisor.core_models.models import Threshold
    thresholds = Threshold.objects.all()
    threshold_count = thresholds.count()
    
    context = {
        'thresholds': thresholds,
        'threshold_count': threshold_count,
        'estimated_rules': threshold_count * 3,  # Each threshold creates 3 rules
    }
    
    return render(request, 'alerts_app/sync_confirm.html', context)


@login_required
def alerts_api(request):
    """API endpoint for alerts data"""
    alerts = AlertInstance.objects.filter(status='active').values(
        'id', 'rule__name', 'router__name', 'severity', 
        'metric_value', 'threshold_value', 'triggered_at'
    )
    
    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert['id'],
            'rule_name': alert['rule__name'],
            'router_name': alert['router__name'],
            'severity': alert['severity'],
            'metric_value': alert['metric_value'],
            'threshold_value': alert['threshold_value'],
            'triggered_at': alert['triggered_at'].isoformat() if alert['triggered_at'] else None,
        })
    
    return JsonResponse({'alerts': alerts_data})


@login_required
def alert_resend_email(request, alert_id):
    """Resend email for an alert"""
    alert = get_object_or_404(AlertInstance, id=alert_id)
    
    if request.method == 'POST':
        # Reset email sent status to allow resending
        alert.email_sent = False
        alert.email_sent_at = None
        alert.save()
        
        # Send email
        if send_alert_email(alert):
            messages.success(request, 'Alert email sent successfully.')
        else:
            messages.error(request, 'Failed to send alert email.')
    
    return redirect('alerts:alert_detail', alert_id=alert.id)
