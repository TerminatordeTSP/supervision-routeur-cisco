from django.urls import path
from .views import index, user_info, appearance, language

urlpatterns = [
    path('', index, name="settings_index"),
    path('user_info/', user_info, name="user_info"),
    path('appearance/', appearance, name="appearance"),
    path('language/', language, name="language")
]