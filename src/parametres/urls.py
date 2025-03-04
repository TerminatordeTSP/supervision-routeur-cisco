from django.urls import path
from parametres.views import index

urlpatterns = [
    path('', index, name='parametre-index'),
]