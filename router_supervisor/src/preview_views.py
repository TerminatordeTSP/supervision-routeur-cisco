from django.shortcuts import render
from django.conf import settings


def preview_404(request):
    """
    Vue pour prévisualiser la page 404 en mode développement
    """
    context = {
        'request_path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
    }
    return render(request, '404.html', context)


def preview_500(request):
    """
    Vue pour prévisualiser la page 500 en mode développement
    """
    context = {
        'request_path': request.path,
    }
    return render(request, '500.html', context)


def preview_403(request):
    """
    Vue pour prévisualiser la page 403 en mode développement
    """
    context = {
        'request_path': request.path,
        'user': request.user,
    }
    return render(request, '403.html', context)
