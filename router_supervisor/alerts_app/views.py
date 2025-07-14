from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import Alert, AlertRule, AlertSeverity, AlertStatus, AlertType
from .services import AlertService
from router_supervisor.core_models.models import Router, KPI


@login_required
def alerts_dashboard(request):
    """Dashboard principal des alertes"""
    
    # Récupérer le résumé des alertes
    summary = AlertService.get_active_alerts_summary()
    
    # Alertes récentes (dernières 24h)
    last_24h = timezone.now() - timedelta(hours=24)
    recent_alerts = Alert.objects.filter(
        created_at__gte=last_24h
    ).order_by('-created_at')[:10]
    
    # Statistiques par routeur
    router_stats = Alert.objects.filter(
        status=AlertStatus.ACTIVE
    ).values(
        'router__name'
    ).annotate(
        alert_count=Count('alert_id')
    ).order_by('-alert_count')[:5]
    
    context = {
        'summary': summary,
        'recent_alerts': recent_alerts,
        'router_stats': router_stats,
        'page_title': 'Dashboard des Alertes'
    }
    
    return render(request, 'alerts_app/dashboard.html', context)


@login_required
def alerts_list(request):
    """Liste des alertes avec filtres"""
    
    alerts = Alert.objects.select_related('router', 'interface', 'kpi').all()
    
    # Filtres
    status_filter = request.GET.get('status')
    severity_filter = request.GET.get('severity')
    router_filter = request.GET.get('router')
    type_filter = request.GET.get('type')
    search = request.GET.get('search')
    
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    
    if router_filter:
        alerts = alerts.filter(router_id=router_filter)
    
    if type_filter:
        alerts = alerts.filter(alert_type=type_filter)
    
    if search:
        alerts = alerts.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(router__name__icontains=search)
        )
    
    # Tri
    sort_by = request.GET.get('sort', '-created_at')
    alerts = alerts.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_alerts = paginator.get_page(page_number)
    
    # Données pour les filtres
    routers = Router.objects.all().order_by('name')
    
    context = {
        'alerts': page_alerts,
        'routers': routers,
        'alert_statuses': AlertStatus.choices,
        'alert_severities': AlertSeverity.choices,
        'alert_types': AlertType.choices,
        'current_filters': {
            'status': status_filter,
            'severity': severity_filter,
            'router': router_filter,
            'type': type_filter,
            'search': search,
            'sort': sort_by,
        },
        'page_title': 'Liste des Alertes'
    }
    
    return render(request, 'alerts_app/alerts_list.html', context)


@login_required
def alert_detail(request, alert_id):
    """Détail d'une alerte"""
    
    alert = get_object_or_404(Alert, alert_id=alert_id)
    
    # Historique de l'alerte
    history = alert.history.all().order_by('-changed_at')
    
    # Alertes similaires (même routeur/KPI dans les dernières 24h)
    similar_alerts = Alert.objects.filter(
        router=alert.router,
        kpi=alert.kpi,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).exclude(alert_id=alert_id).order_by('-created_at')[:5]
    
    context = {
        'alert': alert,
        'history': history,
        'similar_alerts': similar_alerts,
        'page_title': f'Alerte #{alert.alert_id}'
    }
    
    return render(request, 'alerts_app/alert_detail.html', context)


@login_required
@require_POST
def acknowledge_alert(request, alert_id):
    """Acquitter une alerte"""
    
    comment = request.POST.get('comment', '')
    user_email = request.user.email if hasattr(request.user, 'email') else None
    
    success = AlertService.acknowledge_alert(alert_id, user_email, comment)
    
    if success:
        messages.success(request, 'Alerte acquittée avec succès.')
    else:
        messages.error(request, 'Erreur lors de l\'acquittement de l\'alerte.')
    
    return redirect('alerts_app:alert_detail', alert_id=alert_id)


@login_required
@require_POST
def resolve_alert(request, alert_id):
    """Résoudre une alerte"""
    
    comment = request.POST.get('comment', '')
    user_email = request.user.email if hasattr(request.user, 'email') else None
    
    success = AlertService.resolve_alert(alert_id, user_email, comment)
    
    if success:
        messages.success(request, 'Alerte résolue avec succès.')
    else:
        messages.error(request, 'Erreur lors de la résolution de l\'alerte.')
    
    return redirect('alerts_app:alert_detail', alert_id=alert_id)


@login_required
@require_POST
def dismiss_alert(request, alert_id):
    """Ignorer une alerte"""
    
    try:
        alert = get_object_or_404(Alert, alert_id=alert_id)
        alert.dismiss()
        messages.success(request, 'Alerte ignorée avec succès.')
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'action: {str(e)}')
    
    return redirect('alerts_app:alert_detail', alert_id=alert_id)


def api_alerts_summary(request):
    """API pour obtenir le résumé des alertes (pour AJAX)"""
    
    summary = AlertService.get_active_alerts_summary()
    return JsonResponse(summary)


def api_alerts_count(request):
    """API pour obtenir le nombre d'alertes actives"""
    
    count = Alert.get_active_alerts_count()
    critical_count = Alert.get_critical_alerts_count()
    
    return JsonResponse({
        'total_active': count,
        'critical_active': critical_count
    })


@login_required
def alerts_statistics(request):
    """Page de statistiques des alertes"""
    
    # Période par défaut: 30 derniers jours
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Alertes dans la période
    alerts_in_period = Alert.objects.filter(created_at__gte=start_date)
    
    # Statistiques générales
    stats = {
        'total_alerts': alerts_in_period.count(),
        'resolved_alerts': alerts_in_period.filter(status=AlertStatus.RESOLVED).count(),
        'active_alerts': alerts_in_period.filter(status=AlertStatus.ACTIVE).count(),
        'by_severity': {
            severity[0]: alerts_in_period.filter(severity=severity[0]).count()
            for severity in AlertSeverity.choices
        },
        'by_type': {
            alert_type[0]: alerts_in_period.filter(alert_type=alert_type[0]).count()
            for alert_type in AlertType.choices
        },
        'by_router': list(
            alerts_in_period.values('router__name')
            .annotate(count=Count('alert_id'))
            .order_by('-count')[:10]
        )
    }
    
    # Données pour le graphique temporel (par jour)
    daily_stats = []
    for i in range(days):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_alerts = alerts_in_period.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        )
        
        daily_stats.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'total': day_alerts.count(),
            'critical': day_alerts.filter(severity=AlertSeverity.CRITICAL).count(),
            'high': day_alerts.filter(severity=AlertSeverity.HIGH).count(),
        })
    
    daily_stats.reverse()  # Ordre chronologique
    
    context = {
        'stats': stats,
        'daily_stats': daily_stats,
        'days': days,
        'start_date': start_date,
        'page_title': 'Statistiques des Alertes'
    }
    
    return render(request, 'alerts_app/statistics.html', context)
