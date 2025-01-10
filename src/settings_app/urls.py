from django.urls import path
from .views import index

urlpatterns = [
    path('settings/', index, name="settings_index"),
]