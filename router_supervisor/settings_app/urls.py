from django.urls import path
from .views import index, user_info
from .views import index, user_info, register

urlpatterns = [
    path('', index, name="settings_index"),
    path('user_info/', user_info, name="user_info"),
    path('personal_info/', user_info, name="personal_info"),
    path('register/', register, name="register"),
]