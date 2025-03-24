from django import forms
from django.db import models
from config_routeur.models import threshold
from django.core.validators import MinValueValidator

"""
class enter_seuil(forms.Form):
    ram = forms.FloatField(
        min_value=0.1,  # minimum 0.1
        label="RAM en Mo",
        initial=300,  # valeur par défaut
    )
    cpu = forms.FloatField(
        min_value=1,  # minimum 1
        label="cpu utilisé en %",
        initial=50,  # valeur par défaut
    )
    trafic = forms.FloatField(
        min_value=0.001,  # minimum 0.001
        label="Bande passante en Mo/s",
        initial=100,  # valeur par défaut
    )
    nom = forms.CharField(
        max_length=50,
        label="Nom du seuil",
        initial="seuil",  # valeur par défaut
    )
    def clean_ram(self):
        ram = self.cleaned_data.get('ram')
        if ram < 0.1:  # Exemple de condition
            raise forms.ValidationError("La valeur de la RAM doit dépasser 0.1 Mo.")
        return ram

    def clean_cpu(self):
        cpu = self.cleaned_data.get('cpu')
        if cpu > 100:  # cpu ne peut pas dépasser 100%
            raise forms.ValidationError("L'utilisation du cpu doit exceder 1%.")
        return cpu

    def clean_trafic(self):
        trafic = self.cleaned_data.get('trafic')
        if trafic < 0.1:  # Exemple d'une erreur personnalisée pour trafic
            raise forms.ValidationError("Le trafic doit être au minimum de 0.001 Gb/s.")
        return trafic

    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if len(nom.strip()) < 5:  # Exemple : validation du nom
            raise forms.ValidationError("Le nom doit contenir au moins 5 caractères.")
        return nom

"""
"""
class enter_seuil(forms.ModelForm):
    class Meta :
        model = Seuil
        fields = '__all__'
"""

from django import forms
from config_routeur.models import threshold

class enter_threshold(forms.ModelForm):
    ram = forms.FloatField(
        min_value=0.1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez la valeur RAM',
            'step': '0.1'
        })
    )
    cpu = forms.FloatField(
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez la valeur cpu',
            'step': '0.1'
        })
    )
    trafic = forms.FloatField(
        min_value=0.001,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez la valeur du trafic',
            'step': '0.1'
        })
    )
    nom = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le nom du threshold'
        })
    )

    class Meta:
        model = threshold
        fields = ['ram', 'cpu', 'trafic', 'nom']