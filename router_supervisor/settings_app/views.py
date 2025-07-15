from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from router_supervisor.core_models.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from router_supervisor.settings_app.forms import CustomUserCreationForm, UserInfoForm, UserPreferencesForm
from router_supervisor.settings_app.models import UserPreferences

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Vous êtes connecté.")
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def get_or_create_user():
    """Get the first user or create a demo user"""
    user = User.objects.first()
    if not user:
        user = User.objects.create(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='admin',
            role='admin'
        )
    return user


def get_user_preferences(user):
    """Get or create user preferences"""
    preferences, created = UserPreferences.objects.get_or_create(
        user=user,
        defaults={
            'theme': 'orange',
            'language': 'en'
        }
    )
    return preferences

@login_required
def index(request):
    # Use the current logged-in user
    user = request.user
    preferences = get_user_preferences(user)
    
    context = {
        'user': user,
        'preferences': preferences,
    }
    return render(request, "settings/index.html", context)
@login_required
def user_info(request):
    """Vue pour modifier les informations personnelles de l'utilisateur connecté"""
    user = request.user
    print(f"DEBUG: User: {user.email}, First: {user.first_name}, Last: {user.last_name}")
    
    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès!")
            return redirect('/settings/user_info/')
        else:
            print(f"DEBUG: Form errors: {form.errors}")
    else:
        form = UserInfoForm(instance=user)
        print(f"DEBUG: Form initial data: {form.initial}")
    
    preferences = get_user_preferences(user)
    context = {
        'form': form,
        'user': user,
        'preferences': preferences,
    }
    return render(request, "settings/info_user.html", context)


from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    from_email = 'admin@telecom-sudparis.eu'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    extra_email_context = {
        'domain': 'z.imt.fr',
        'protocol': 'https'
    }

@login_required
def preferences(request):
    """Vue pour modifier les préférences de l'utilisateur connecté"""
    user = request.user
    user_preferences = get_user_preferences(user)
    
    if request.method == 'POST':
        preferences_form = UserPreferencesForm(request.POST, instance=user_preferences)
        if preferences_form.is_valid():
            preferences_form.save()
            messages.success(request, "Vos préférences ont été mises à jour avec succès!")
            return redirect('/settings/preferences/')
    else:
        preferences_form = UserPreferencesForm(instance=user_preferences)
    
    context = {
        'preferences_form': preferences_form,
        'user': user,
        'preferences': user_preferences,
    }
    return render(request, "settings/preferences.html", context)


@login_required
def appearance(request):
    """Vue pour modifier l'apparence (thème)"""
    user = request.user
    user_preferences = get_user_preferences(user)
    
    if request.method == 'POST':
        theme = request.POST.get('theme')
        if theme in ['orange', 'blue', 'green']:
            user_preferences.theme = theme
            user_preferences.save()
            messages.success(request, "Thème mis à jour avec succès!")
        return redirect('/settings/appearance/')
    
    context = {
        'user': user,
        'preferences': user_preferences,
    }
    return render(request, "settings/appearance.html", context)


@login_required
def language(request):
    """Vue pour modifier la langue"""
    user = request.user
    user_preferences = get_user_preferences(user)
    
    if request.method == 'POST':
        language = request.POST.get('language')
        if language in ['en', 'fr', 'es']:
            user_preferences.language = language
            user_preferences.save()
            messages.success(request, "Langue mise à jour avec succès!")
        return redirect('/settings/language/')
    
    context = {
        'user': user,
        'preferences': user_preferences,
    }
    return render(request, "settings/language.html", context)