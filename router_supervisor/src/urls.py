from django.http import HttpResponse
from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from django.conf import settings
from django.conf.urls.static import static
import sys, os
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from django.urls import path
from router_supervisor.settings_app.views import CustomPasswordResetView
from django.contrib.auth import views as auth_views
# Import des gestionnaires d'erreur personnalisés
from . import error_views

# Add the current directory to the Python path to find the apps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def health_check(request):
    return HttpResponse("Alive and well")

def test_static_direct(request):
    return HttpResponse("Static endpoint test works!")

def test_404(request):
    """Vue de test pour la page 404"""
    from django.http import Http404
    raise Http404("Page de test pour l'erreur 404")

def test_500(request):
    """Vue de test pour la page 500"""
    raise Exception("Erreur de test pour la page 500")

def test_403(request):
    """Vue de test pour la page 403"""
    from django.core.exceptions import PermissionDenied
    raise PermissionDenied("Test de permission refusée")

urlpatterns = [
    path('', include("router_supervisor.dashboard_app.urls")),
    path('admin/', admin.site.urls),
    path('settings/', include("router_supervisor.settings_app.urls")),
    path('thresholds/', include('router_supervisor.thresholds_app.urls')),
    path('api/', include('router_supervisor.api_app.urls')),
    path('health/', health_check, name='health_check'),
    path('test-static-direct/', test_static_direct, name='test_static_direct'),
    path('test-404/', test_404, name='test_404'),
    path('test-500/', test_500, name='test_500'),
    path('test-403/', test_403, name='test_403'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('password-reset/',
     auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),
     name='password_reset'),

    path('password-reset/done/',
     auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
     name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
     name='password_reset_confirm'),

    path('reset/done/',
     auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
     name='password_reset_complete'),

path(
        'password-reset/',
        CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Serve static files in production using Django's built-in helper
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configuration des gestionnaires d'erreur
handler404 = error_views.custom_404_view
#handler500 = error_views.custom_500_view
handler500 = 'django.views.defaults.server_error'
handler403 = error_views.custom_403_view

# Vues de prévisualisation des pages d'erreur (seulement en mode DEBUG)
if settings.DEBUG:
    from . import preview_views
    urlpatterns += [
        path('preview-404/', preview_views.preview_404, name='preview_404'),
        path('preview-500/', preview_views.preview_500, name='preview_500'),
        path('preview-403/', preview_views.preview_403, name='preview_403'),
    ]
