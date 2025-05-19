from thresholds_app import views
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

urlpatterns = [
    path('', include("router_supervisor.dashboard_app.urls")),
    path('admin/', admin.site.urls),
    path('settings/', include("router_supervisor.settings_app.urls")),
    path('thresholds/', include('router_supervisor.thresholds_app.urls')),
    path('api/', include('router_supervisor.api_app.urls')),
    path('health/', health_check, name='health_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
