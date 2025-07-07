from django.urls import path
from . import views


urlpatterns = [
    # Accueil ou liste globale
    path('', views.configuration, name='configuration'),

    # Router details
    path('router/<int:router_id>/', views.configuration_router_detail, name='configuration_router_detail'),

    # Router creation
    path('router/', views.routers, name='routers'),

    # Router update
    path('router/update/<int:id>/', views.router_update, name='router_update'),

    # Router delete
    path('router/delete/<int:id>/', views.router_delete, name='router_delete'),

    # Threshold details
    path('threshold/<int:th_id>/', views.configuration_threshold_detail, name='configuration_threshold_detail'),

    # Threshold creation
    path('threshold/', views.thresholds, name='thresholds'),

    # Threshold update
    path('threshold/update/<int:id>/', views.threshold_update, name='threshold_update'),

    # Threshold delete
    path('threshold/delete/<int:id>/', views.threshold_delete, name='threshold_delete'),
]