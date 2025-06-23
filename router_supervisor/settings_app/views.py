from django.shortcuts import render, redirect # type: ignore
from .forms import UserInfoForm
from django.contrib.auth.models import User

def index(request):
    return render(request,"settings/base.html")

def user_info(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = UserInfoForm(request.POST, instance=request.user)
        else:
            form = UserInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/settings/user_info/')
    else:
        if request.user.is_authenticated:
            form = UserInfoForm(instance=request.user)
        else:
            form = UserInfoForm()

    return render(request, "settings/info_user.html", {'form': form})

def appearance(request):
    return render(request,"settings/appearance.html")

def language(request):
    return render(request,"settings/language.html")