from django import forms
from django.db import models

from django.core.validators import MinValueValidator


class enter_seuil(forms.Form):
    ram = forms.FloatField(
        min_value=0.1,  # minimum 0.1
        label="RAM en Mo",
        initial=300,  # valeur par défaut
    )
    CPU = forms.FloatField(
        min_value=1,  # minimum 1
        label="CPU utilisé en %",
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

    def clean_CPU(self):
        CPU = self.cleaned_data.get('CPU')
        if CPU > 100:  # CPU ne peut pas dépasser 100%
            raise forms.ValidationError("L'utilisation du CPU doit exceder 1%.")
        return CPU

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
