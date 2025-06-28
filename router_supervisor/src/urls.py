from django.http import HttpResponse
from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from django.conf import settings
from django.conf.urls.static import static
import sys, os

# Add the current directory to the Python path to find the apps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def health_check(request):
    return HttpResponse("Alive and well")

def test_static_direct(request):
    return HttpResponse("Static endpoint test works!")

urlpatterns = [
    path('', include("dashboard_app.urls")),
    path('admin/', admin.site.urls),
    path('settings/', include("settings_app.urls")),
    path('thresholds/', include('thresholds_app.urls')),
    path('api/', include('api_app.urls')),
    path('health/', health_check, name='health_check'),
    path('test-static-direct/', test_static_direct, name='test_static_direct'),
]

# Serve static files in production using Django's built-in helper
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
