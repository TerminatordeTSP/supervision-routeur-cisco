from django.urls import path
from . import views

urlpatterns = [
    path('', views.configuration, name='configuration'),
    path('router/<int:id>/', views.configuration_router_config, name='configuration_router_config'),
    path('threshold/<int:th_id>/', views.configuration_threshold_detail, name='configuration_threshold_detail'),
    path('threshold/', views.thresholds, name='thresholds'),
    path('update/<int:id>/', views.threshold_update, name='threshold_update'),
    path('threshold/delete/<int:id>/', views.threshold_delete, name='threshold_delete'),
]