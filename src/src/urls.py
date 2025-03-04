"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from config_routeur import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('config_routeur01/', views.index),
    path('configuration/', views.configuration, name='configuration'),
    path('configuration/routeur/<int:id>/', views.configuration_routeur_detail, name='configuration_routeur_detail'),
    path('configuration/seuil/<int:id>/', views.configuration_seuil_detail, name='configuration_seuil_detail'),
    path('configuration/seuil/', views.seuils, name='seuil'),
    path('configuration/seuil_update/<int:id>/', views.seuil_update, name='seuil_update'),
    path('configuration/seuil_delate/<int:id>/', views.band_delete, name='seuil_delate'),
]

