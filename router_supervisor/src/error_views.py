from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden


def custom_404_view(request, exception):
    """
    Vue personnalisée pour l'erreur 404
    """
    return HttpResponseNotFound(
        render(request, '404.html', {
            'request_path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }).content
    )


def custom_500_view(request):
    """
    Vue personnalisée pour l'erreur 500
    """
    return HttpResponseServerError(
        render(request, '500.html', {
            'request_path': request.path,
        }).content
    )


def custom_403_view(request, exception):
    """
    Vue personnalisée pour l'erreur 403
    """
    return HttpResponseForbidden(
        render(request, '403.html', {
            'request_path': request.path,
            'user': request.user,
        }).content
    )
