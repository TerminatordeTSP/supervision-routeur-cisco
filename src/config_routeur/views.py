from django.shortcuts import render
from config_routeur.models import Routeur
from config_routeur.models import Seuil
from config_routeur.forms import enter_seuil



def index(request):
    return render(request, 'routeur01.html')

def configuration(request):
    routeurs = Routeur.objects.all()
    seuils = Seuil.objects.all()
    return render(request, 'Page de configuration.html',{'routeurs': routeurs,'seuils':seuils})

def configuration_routeur_detail(request, id):  # notez le paramètre id supplémentaire
   routeur = Routeur.objects.get(id=id)
   return render(request,
          'routeur_detail.html',
                 {'routeur': routeur}) # nous passons l'id au modèle

def configuration_seuil_detail(request, id):  # notez le paramètre id supplémentaire
   seuil = Seuil.objects.get(id=id)
   return render(request,
          'seuil_detail.html',
                 {'seuil': seuil}) # nous passons l'id au modèle

def seuils(request):
  form = enter_seuil()
  return render(request,
          'seuil.html',
          {'form': form})