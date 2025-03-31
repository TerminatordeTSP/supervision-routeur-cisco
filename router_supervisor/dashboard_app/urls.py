from django.urls import path, include
from .views import index

urlpatterns = [
    path('', index, name="dashboard_index"),
    # path('dashboard/', include("dashboard_app.urls")),
]