from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from thresholds_app.models import Router, Threshold
from thresholds_app.forms import threshold_insert
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.contrib import messages
from .models import Router, Threshold
from .forms import RouterForm

def index(request):
    return render(request, 'config.html')

def configuration(request):
    routers = Router.objects.all()
    thresholds = Threshold.objects.all()
    return render(request, 'config.html', {'routers': routers, 'thresholds': thresholds})

def configuration_router_config(request, id):
    router = Router.objects.get(id=id)
    return render(request,
                  'router_config.html',
                  {'router': router})

def configuration_threshold_detail(request, th_id):
    threshold = Threshold.objects.get(threshold_id=th_id)
    return render(request,
                  'threshold_detail.html',
                  {
                      'threshold': threshold,
                      'threshold_id': threshold.threshold_id  # 👈 Ajoute ça
                  })
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
                  'threshold_update.html',
                  {'form': form})

def threshold_update(request, id):
    threshold = get_object_or_404(Threshold, threshold_id=id)

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

def threshold_delete(request, id):
    threshold = get_object_or_404(Threshold, threshold_id=id)

    if request.method == 'POST':
        threshold.delete()
        messages.success(request, f"Threshold '{threshold.name}' successfully deleted.")
        return redirect('configuration')

    return render(request,
                  'threshold_confirm_delete.html',
                  {'threshold': threshold})

def configuration_router_detail(request, router_id):
    router = get_object_or_404(Router, router_id=router_id)
    return render(request,
                  'router_detail.html',
                  {
                      'router': router,
                      'router_id': router.router_id
                  })

def routers(request):
    if request.method == 'POST':
        form = RouterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            ip_address = form.cleaned_data['ip_address']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            secret = form.cleaned_data['secret']
            threshold = form.cleaned_data['threshold']

            try:
                if Router.objects.filter(name=name).exists():
                    form.add_error(None, f"Error: A router with the name '{name}' already exists.")
                else:
                    router = Router(
                        name=name,
                        ip_address=ip_address,
                        username=username,
                        password=password,
                        secret=secret,
                        threshold=threshold
                    )
                    router.save()
                    return redirect('configuration')
            except IntegrityError as e:
                form.add_error(None, f"Error creating router: {str(e)}")
    else:
        form = RouterForm()

    return render(request,
                  'router_update.html',
                  {'form': form, 'thresholds': Threshold.objects.all()})

def routers(request):
    if request.method == 'POST':
        form = RouterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            ip_address = form.cleaned_data['ip_address']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            secret = form.cleaned_data['secret']
            threshold = form.cleaned_data['threshold']

            try:
                if Router.objects.filter(name=name).exists():
                    form.add_error(None, f"Error: A router with the name '{name}' already exists.")
                else:
                    router = Router(
                        name=name,
                        ip_address=ip_address,
                        username=username,
                        password=password,
                        secret=secret,
                        threshold=threshold
                    )
                    router.save()
                    return redirect('configuration')
            except IntegrityError as e:
                form.add_error(None, f"Error creating router: {str(e)}")
    else:
        form = RouterForm()

    return render(request,
                  'router_update.html',
                  {'form': form, 'thresholds': Threshold.objects.all()})

def router_update(request, id):
    router = get_object_or_404(Router, router_id=id)

    if request.method == 'POST':
        form = RouterForm(request.POST, instance=router)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Router successfully updated.')
                return redirect('configuration')
            except Exception as e:
                messages.error(request, f'Error during update: {str(e)}')
    else:
        form = RouterForm(instance=router)

    return render(request,
                  'router_update.html',
                  {
                      'form': form,
                      'router': router,
                      'thresholds': Threshold.objects.all(),
                      'router_id': router.router_id
                  })

def router_delete(request, id):
    router = get_object_or_404(Router, router_id=id)

    if request.method == 'POST':
        router.delete()
        messages.success(request, f"Router '{router.name}' successfully deleted.")
        return redirect('configuration')

    return render(request,
                  'router_confirm_delete.html',
                  {'router': router})

