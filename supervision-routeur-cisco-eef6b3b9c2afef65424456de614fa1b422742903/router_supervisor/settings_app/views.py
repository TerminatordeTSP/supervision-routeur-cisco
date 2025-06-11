from django.shortcuts import render, redirect # type: ignore
from .forms import UserInfoForm
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,"settings/index.html")

@login_required
def user_info(request):
    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/settings/user_info/')
    else:
        form = UserInfoForm(instance=request.user)

    return render(request, "settings/info_user.html", {'form': form})

def appearance(request):
    return render(request,"settings/appearance.html")

def language(request):
    return render(request,"settings/language.html")