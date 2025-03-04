from django.contrib import admin
from django.urls import path, include
from config_routeur import views
from src.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),  # Page d’accueil
    path('config_routeur01/', views.index),
    path('configuration/', views.configuration, name='configuration'),
    path('configuration/routeur/<int:id>/', views.configuration_routeur_detail, name='configuration_routeur_detail'),
    path('configuration/seuil/<int:id>/', views.configuration_seuil_detail, name='configuration_seuil_detail'),
    path('configuration/seuil/', views.seuils, name='seuil'),
    path('configuration/seuil_update/<int:id>/', views.seuil_update, name='seuil_update'),
    path('settings/', include('settings_app.urls')),  # Fusionne settings_app avec parametres
    path('settings/', include('parametres.urls')),  
    path('dashboard/', include('dashboard.urls')),
]