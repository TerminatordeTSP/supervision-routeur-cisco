from django import forms
from django.contrib.auth.forms import UserCreationForm
from router_supervisor.core_models.models import User
from router_supervisor.settings_app.models import UserPreferences


class CustomUserCreationForm(UserCreationForm):
    """Formulaire de création d'utilisateur personnalisé"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserInfoForm(forms.ModelForm):
    """Formulaire pour modifier les informations personnelles"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
        }


class UserPreferencesForm(forms.ModelForm):
    """Formulaire pour modifier les préférences utilisateur"""
    
    class Meta:
        model = UserPreferences
        fields = ['theme', 'language']
        widgets = {
            'theme': forms.Select(attrs={
                'class': 'form-control'
            }),
            'language': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'theme': 'Thème',
            'language': 'Langue',
        }