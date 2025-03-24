from sqlite3 import IntegrityError
from django.shortcuts import redirect
from django.shortcuts import render
from config_routeur.models import Routeur
from config_routeur.models import threshold
from config_routeur.forms import enter_threshold



def index(request):
    return render(request, 'routeur01.html')

def configuration(request):
    routeurs = Routeur.objects.all()
    thresholds = Threshold.objects.all()
    return render(request, 'Page de configuration.html',{'routeurs': routeurs,'seuils':thresholds})

def configuration_routeur_detail(request, id):  # notez le paramètre id supplémentaire
   routeur = Routeur.objects.get(id=id)
   return render(request,
          'routeur_detail.html',
                 {'routeur': routeur}) # nous passons l'id au modèle

def configuration_threshold_detail(request, id):  # notez le paramètre id supplémentaire
   threshold = Threshold.objects.get(id=id)
   return render(request,
          'seuil_detail.html',
                 {'threshold': threshold}) # nous passons l'id au modèle

def thresholds(request):
    if request.method == 'POST':
        # créer une instance de notre formulaire et le remplir avec les données POST
        form = enter_threshold(request.POST)
        #print("recup : ",form)
    else:
        # ceci doit être une requête GET, donc créer un formulaire vide
        form = enter_threshold()
    if form.is_valid():
        cpu=form.cleaned_data['cpu']
        ram=form.cleaned_data['ram']
        trafic=form.cleaned_data['trafic']
        nom=form.cleaned_data['nom']
        try:
            if Threshold.objects.filter(nom=nom).exists():
                form.add_error(None,f"Erreur : un threshold avec le nom '{nom}' existe déjà.")
            else:
                threshold = Threshold(cpu=cpu, ram=ram, trafic=trafic, nom=nom)
                threshold.save()
                return configuration(request)
        except IntegrityError as e:
            form.add_error(None, f"Erreur : un seuil avec le nom '{nom}' existe déjà.")

    return render(request,
          'threshold.html',
          {'form': form})
"""
def seuil_update(request, id):
    seuil = Seuil.objects.get(id=id)
    form = enter_seuil(instance=seuil)  # on pré-remplir le formulaire avec un groupe existant
    return render(request,
                  'seuil-update.html',
                  {'form': form})
"""
"""
def seuil_update(request, id):
    seuil = Seuil.objects.get(id=id)

    if request.method == 'POST':
        form = enter_seuil(request.POST, instance=seuil)
        if form.is_valid():
            # mettre à jour le groupe existant dans la base de données
            form.save()
            # rediriger vers la page détaillée du groupe que nous venons de mettre à jour
            return configuration(request)
    else:
        form = enter_seuil(instance=seuil)

    return render(request,
                  'seuil2.html',
                  {'form': form})

"""
"""
def seuil_update(request, id):
    seuil = Seuil.objects.get(id=id)

    if request.method == 'POST':
        form = enter_seuil(request.POST, instance=seuil)
        if form.is_valid():
            # mettre à jour le groupe existant dans la base de données
            form.save()
            # rediriger vers la page détaillée du groupe que nous venons de mettre à jour
            return configuration(request)
    else:
        form = enter_seuil(instance=seuil)

    return render(request,
                  'seuil-update.html',
                  {'form': form})
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from config_routeur.models import Threshold
from config_routeur.forms import enter_threshold

def threshold_update(request, id):
    threshold = get_object_or_404(threshold, id=id)

    if request.method == 'POST':
        form = enter_threshold(request.POST, instance=threshold)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Seuil modifié avec succès.')
                return redirect('configuration')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
    else:
        form = enter_threshold(instance=threshold)

    return render(request,
                 'threshold2.html',
                 {'form': form, 'threshold': threshold})