from django.urls import path, include
from .views import index
from django.urls import path
from .views import latest_metrics_api

urlpatterns = [
    path('', index, name="dashboard_index"),
    path('api/latest-metrics/', latest_metrics_api, name='latest_metrics_api'),
    # path('dashboard/', include("dashboard_app.urls")),
]