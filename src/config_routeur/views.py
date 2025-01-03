from django.shortcuts import render
from config_routeur.models import Routeur
from config_routeur.models import Seuil

def index(request):
    return render(request, 'routeur01.html')

def configuration(request):
    routeurs = Routeur.objects.all()
    seuils = Seuil.objects.all()
    return render(request, 'Page de configuration.html',{'routeurs': routeurs,'seuils':seuils})