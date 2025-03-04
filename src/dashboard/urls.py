from django.urls import path
from dashboard.views import index
from dashboard.views import receive_telegraf_data

urlpatterns = [
    path('', index, name='dashboard-index'),
    path('telegraf/', receive_telegraf_data, name='receive-telegraf-data'),
]