from django.urls import path
from . import views

app_name = 'dashboard1'  # Namespace pour l'application

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
]