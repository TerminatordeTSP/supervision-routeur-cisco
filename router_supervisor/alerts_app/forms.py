from django import forms
from .models import AlertRule, AlertInstance


class AlertRuleForm(forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = ['name', 'description', 'metric', 'condition', 'threshold_value', 
                 'is_active', 'email_enabled', 'email_recipients']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter rule name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'metric': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'threshold_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'email_recipients': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'user1@example.com, user2@example.com'
            }),
        }


class AlertAcknowledgeForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional comment...'
        }),
        required=False
    )


class AlertResolveForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Resolution comment...'
        }),
        required=False
    )
