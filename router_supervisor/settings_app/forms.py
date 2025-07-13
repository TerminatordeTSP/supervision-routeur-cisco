from django import forms
from django.contrib.auth.forms import UserCreationForm
from router_supervisor.core_models.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')