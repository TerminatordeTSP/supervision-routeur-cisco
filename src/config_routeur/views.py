from django.shortcuts import render

def index(request):
    return render(request, 'routeur01.html')

