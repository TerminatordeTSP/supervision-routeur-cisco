from django.contrib import admin
from django.urls import path, include
from config_routeur import views
from src.views import index
from alerts.views import show_alerts  # Importation de show_alerts depuis feature-alerts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),  # Page d’accueil
    path('alerts/', show_alerts, name='show_alerts'),  # Ajout depuis feature-alerts
    path('config_routeur01/', views.index),
    path('configuration/', views.configuration, name='configuration'),
    path('configuration/routeur/<int:id>/', views.configuration_routeur_detail, name='configuration_routeur_detail'),
    path('configuration/threshold/<int:id>/', views.configuration_threshold_detail, name='configuration_threshold_detail'),
    path('configuration/threshold/', views.thresholds, name='threshold'),
    path('configuration/threshold_update/<int:id>/', views.threshold_update, name='threshold_update'),
    path('settings/', include('settings_app.urls')),  
    path('settings/', include('parametres.urls')),  
    path('dashboard/', include('dashboard.urls')),
]