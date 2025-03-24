from django.shortcuts import render


def dashboard_view(request):
    # Ajoutez ici toute logique nécessaire, comme la récupération de données
    # context = {'some_data': data}
    return render(request, 'dashboard1/dashboard.html')  # , context)


from django.shortcuts import render

# Create your views here.
