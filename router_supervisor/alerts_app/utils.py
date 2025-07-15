from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import AlertInstance, AlertRule, AlertHistory
from router_supervisor.core_models.models import RouterMetricLog, Router
import logging


logger = logging.getLogger(__name__)


def send_alert_email(alert):
    """Send email notification for an alert"""
    if not alert.rule.email_enabled or alert.email_sent:
        return False
    
    # Get email recipients
    recipients = []
    if alert.rule.email_recipients:
        recipients = [email.strip() for email in alert.rule.email_recipients.split(',')]
    
    # Add user's email if they have alerts enabled
    if hasattr(alert.router, 'user_router_set'):
        for user_router in alert.router.user_router_set.all():
            user_email = user_router.user.email
            if user_email and user_email not in recipients:
                recipients.append(user_email)
    
    if not recipients:
        logger.warning(f"No recipients found for alert {alert.id}")
        return False
    
    try:
        # Prepare email content
        subject = f"[ALERT] {alert.rule.name} - {alert.router.name}"
        
        context = {
            'alert': alert,
            'router': alert.router,
            'rule': alert.rule,
        }
        
        message = render_to_string('alerts_app/alert_email.txt', context)
        html_message = render_to_string('alerts_app/alert_email.html', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'alerts@routersupervision.com'),
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )
        
        # Mark as sent
        alert.email_sent = True
        alert.email_sent_at = timezone.now()
        alert.save()
        
        logger.info(f"Alert email sent for alert {alert.id} to {recipients}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send alert email for alert {alert.id}: {str(e)}")
        return False


def check_thresholds_and_create_alerts():
    """Check current metrics against alert rules and create alerts if needed"""
    active_rules = AlertRule.objects.filter(is_active=True)
    
    for rule in active_rules:
        # Get all routers
        routers = Router.objects.all()
        
        for router in routers:
            # Get latest metric value for this router
            latest_metric = get_latest_metric_value(router, rule.metric)
            
            if latest_metric is None:
                continue
                
            # Check if threshold is exceeded
            threshold_exceeded = check_threshold(
                latest_metric, 
                rule.threshold_value, 
                rule.condition
            )
            
            if threshold_exceeded:
                # Check if there's already an active alert for this rule/router
                existing_alert = AlertInstance.objects.filter(
                    rule=rule,
                    router=router,
                    status='active'
                ).first()
                
                if not existing_alert:
                    # Create new alert
                    severity = determine_severity(latest_metric, rule.threshold_value, rule.metric)
                    
                    alert = AlertInstance.objects.create(
                        rule=rule,
                        router=router,
                        severity=severity,
                        message=f"{rule.metric.upper()} usage ({latest_metric}%) exceeds threshold ({rule.threshold_value}%)",
                        metric_value=latest_metric,
                        threshold_value=rule.threshold_value
                    )
                    
                    # Send email notification
                    send_alert_email(alert)
                    
                    logger.info(f"Created alert {alert.id} for {router.name}: {rule.name}")


def get_latest_metric_value(router, metric_name):
    """Get the latest metric value for a router from the API data"""
    try:
        # Import here to avoid circular imports
        from router_supervisor.api_app.views import get_latest_metrics
        from django.test import RequestFactory
        
        # Create a fake request to call the API view
        factory = RequestFactory()
        request = factory.get('/api/latest_metrics/')
        
        # Get the latest metrics
        response = get_latest_metrics(request)
        if response.status_code != 200:
            return None
            
        import json
        data = json.loads(response.content)
        
        # Map metric names to field names in the API response
        metric_mapping = {
            'cpu': 'cpu_0_usage',
            'ram': 'memory_usage',
            'traffic': 'bandwidth_usage'
        }
        
        field_name = metric_mapping.get(metric_name)
        if not field_name:
            return None
        
        # Find the metric for this router
        for metric in data:
            if (metric.get('field') == field_name and 
                metric.get('tags', {}).get('hostname') == router.name):
                return float(metric.get('value', 0))
                
    except Exception as e:
        logger.error(f"Error getting metric {metric_name} for router {router.name}: {str(e)}")
    
    return None


def check_threshold(value, threshold, condition):
    """Check if value meets the threshold condition"""
    if condition == 'gt':
        return value > threshold
    elif condition == 'gte':
        return value >= threshold
    elif condition == 'lt':
        return value < threshold
    elif condition == 'lte':
        return value <= threshold
    return False


def determine_severity(value, threshold, metric):
    """Determine alert severity based on how much the threshold is exceeded"""
    if value <= threshold:
        return 'low'
    
    excess_percentage = ((value - threshold) / threshold) * 100
    
    if excess_percentage > 50:
        return 'critical'
    elif excess_percentage > 25:
        return 'high'
    elif excess_percentage > 10:
        return 'medium'
    else:
        return 'low'


def acknowledge_alert(alert, user, comment=''):
    """Acknowledge an alert"""
    if alert.status == 'active':
        old_status = alert.status
        alert.status = 'acknowledged'
        alert.acknowledged_by = user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        # Create history entry
        AlertHistory.objects.create(
            alert=alert,
            old_status=old_status,
            new_status='acknowledged',
            changed_by=user,
            comment=comment
        )
        
        return True
    return False


def resolve_alert(alert, user, comment=''):
    """Resolve an alert"""
    if alert.status in ['active', 'acknowledged']:
        old_status = alert.status
        alert.status = 'resolved'
        alert.resolved_by = user
        alert.resolved_at = timezone.now()
        alert.save()
        
        # Create history entry
        AlertHistory.objects.create(
            alert=alert,
            old_status=old_status,
            new_status='resolved',
            changed_by=user,
            comment=comment
        )
        
        return True
    return False
