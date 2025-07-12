from django import forms
from router_supervisor.core_models.models import User
from .models import UserPreferences

class UserInfoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

class AppearanceForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['theme']
        widgets = {
            'theme': forms.RadioSelect(attrs={'class': 'theme-radio'})
        }

class LanguageForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['language']
        widgets = {
            'language': forms.RadioSelect(attrs={'class': 'language-radio'})
        }
