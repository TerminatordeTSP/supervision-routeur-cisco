from django.shortcuts import render


def index(request):
    return render(request,"settings/index.html")

def user_info(request):
    return render(request,"settings/info_user.html")

def appearance(request):
    return render(request,"settings/appearance.html")

def language(request):
    return render(request,"settings/language.html")