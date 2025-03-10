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
    path('configuration/seuil/<int:id>/', views.configuration_seuil_detail, name='configuration_seuil_detail'),
    path('configuration/seuil/', views.seuils, name='seuil'),
    path('configuration/seuil_update/<int:id>/', views.seuil_update, name='seuil_update'),
    path('settings/', include('settings_app.urls')),  
    #path('settings/', include('parametres.urls')),  à supprimer
    path('dashboard/', include('dashboard.urls')),
]