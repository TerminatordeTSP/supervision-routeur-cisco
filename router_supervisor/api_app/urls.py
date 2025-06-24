from django.urls import path
from .views import receive_metrics, get_latest_metrics

urlpatterns = [
    path('receive-metrics/', receive_metrics, name='receive_metrics'),
    path('latest-metrics/', get_latest_metrics, name='get_latest_metrics'),
]