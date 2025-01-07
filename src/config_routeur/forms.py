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
