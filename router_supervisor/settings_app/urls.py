from django.urls import path
from .views import index, user_info, register, preferences, appearance, language

urlpatterns = [
    path('', index, name="settings_index"),
    path('user_info/', user_info, name="user_info"),
    path('personal_info/', user_info, name="personal_info"),
    path('preferences/', preferences, name="preferences"),
    path('appearance/', appearance, name="appearance"),
    path('language/', language, name="language"),
    path('register/', register, name="register"),
]