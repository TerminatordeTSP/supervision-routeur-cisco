from django.urls import path, include
from .views import index
from django.urls import path
from .views import latest_metrics_api
from . import views

urlpatterns = [
    path('', index, name="dashboard_index"),
    #path('api/latest-metrics/', latest_metrics_api, name='latest_metrics_api'),
    # path('dashboard/', include("dashboard_app.urls")),
    path('api/latest_metrics/', views.get_latest_metrics, name='latest_metrics'),
]