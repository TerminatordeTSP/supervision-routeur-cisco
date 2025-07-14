from django.urls import path
from . import views

app_name = 'alerts_app'

urlpatterns = [
    # Dashboard et listes
    path('', views.alerts_dashboard, name='dashboard'),
    path('list/', views.alerts_list, name='alerts_list'),
    path('statistics/', views.alerts_statistics, name='statistics'),
    
    # Détails et actions sur les alertes
    path('alert/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('alert/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('alert/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('alert/<int:alert_id>/dismiss/', views.dismiss_alert, name='dismiss_alert'),
    
    # Intégration avec les seuils (thresholds)
    # Les règles d'alertes sont gérées via l'app thresholds_app
    
    # API endpoints
    path('api/summary/', views.api_alerts_summary, name='api_summary'),
    path('api/count/', views.api_alerts_count, name='api_count'),
]
