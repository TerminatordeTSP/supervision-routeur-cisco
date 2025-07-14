from django import forms
from router_supervisor.core_models.models import Router, Threshold

class threshold_insert(forms.ModelForm):
    ram = forms.FloatField(
        min_value=0.1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter RAM value',
            'step': '0.1'
        })
    )
    cpu = forms.FloatField(
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter CPU value',
            'step': '0.1'
        })
    )
    traffic = forms.FloatField(
        min_value=0.001,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter traffic value',
            'step': '0.1'
        })
    )
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter threshold name'
        })
    )

    class Meta:
        model = Threshold
        fields = ['ram', 'cpu', 'traffic', 'name']


class RouterForm(forms.ModelForm):
    threshold = forms.ModelChoiceField(
        queryset=Threshold.objects.all(),
        required=False,
        empty_label="No threshold",
        widget = forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Router
        fields = ['name', 'ip_address', 'username', 'password', 'secret', 'threshold']