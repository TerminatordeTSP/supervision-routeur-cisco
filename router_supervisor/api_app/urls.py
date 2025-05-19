from django.urls import path
from .views import receive_metrics

urlpatterns = [
    path('metrics/', receive_metrics, name='receive_metrics'),
]