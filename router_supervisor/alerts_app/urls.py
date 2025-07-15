from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Main alerts views
    path('', views.alerts_index, name='alerts_index'),
    path('alert/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('alert/<int:alert_id>/acknowledge/', views.alert_acknowledge, name='alert_acknowledge'),
    path('alert/<int:alert_id>/resolve/', views.alert_resolve, name='alert_resolve'),
    path('alert/<int:alert_id>/resend-email/', views.alert_resend_email, name='alert_resend_email'),
    
    # Alert rules management (read-only)
    path('rules/', views.rules_index, name='rules_index'),
    path('rules/<int:rule_id>/', views.rule_detail, name='rule_detail'),
    path('rules/sync/', views.sync_rules_from_thresholds, name='sync_rules'),
    
    # API endpoints
    path('api/alerts/', views.alerts_api, name='alerts_api'),
]
