from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from thresholds_app.models import Router, Threshold
from thresholds_app.forms import threshold_insert

def index(request):
    return render(request, 'router01.html')

def configuration(request):
    routers = Router.objects.all()
    thresholds = Threshold.objects.all()
    return render(request, 'config.html', {'routers': routers, 'thresholds': thresholds})

def configuration_router_config(request, id):
    router = Router.objects.get(id=id)
    return render(request,
                  'router_config.html',
                  {'router': router})

def configuration_threshold_detail(request, id):
    threshold = Threshold.objects.get(id=id)
    return render(request,
                  'threshold_detail.html',
                  {'threshold': threshold})

def thresholds(request):
    if request.method == 'POST':
        form = threshold_insert(request.POST)
    else:
        form = threshold_insert()
    if form.is_valid():
        cpu = form.cleaned_data['cpu']
        ram = form.cleaned_data['ram']
        traffic = form.cleaned_data['traffic']
        name = form.cleaned_data['name']
        try:
            if Threshold.objects.filter(name=name).exists():
                form.add_error(None, f"Error: A threshold with the name '{name}' already exists.")
            else:
                threshold = Threshold(cpu=cpu, ram=ram, traffic=traffic, name=name)
                threshold.save()
                return configuration(request)
        except IntegrityError as e:
            form.add_error(None, f"Error: A threshold with the name '{name}' already exists.")

    return render(request,
                  'threshold_detail.html',
                  {'form': form})

def threshold_update(request, id):
    threshold = get_object_or_404(Threshold, id=id)

    if request.method == 'POST':
        form = threshold_insert(request.POST, instance=threshold)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Threshold successfully updated.')
                return redirect('configuration')
            except Exception as e:
                messages.error(request, f'Error during update: {str(e)}')
    else:
        form = threshold_insert(instance=threshold)

    return render(request,
                  'threshold_update.html',
                  {'form': form, 'threshold': threshold})