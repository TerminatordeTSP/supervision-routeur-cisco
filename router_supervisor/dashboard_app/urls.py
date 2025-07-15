from django.urls import path, include
from .views import index
from django.urls import path
from .views import latest_metrics_api
from . import views

urlpatterns = [
    path('', index, name="dashboard_index"),
    path('api/latest-metrics/', views.latest_metrics_api, name='latest_metrics_api'),
    # path('dashboard/', include("dashboard_app.urls")),
    path('api/latest_metrics/', views.latest_metrics_api, name='latest_metrics'),
]