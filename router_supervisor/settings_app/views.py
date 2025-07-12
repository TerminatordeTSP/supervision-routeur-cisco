from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from router_supervisor.core_models.models import User
from .forms import UserInfoForm, AppearanceForm, LanguageForm
from .models import UserPreferences
from django.contrib.auth.decorators import login_required

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
@login_required
def get_user_preferences(user):
    """Get or create user preferences"""
    preferences, created = UserPreferences.objects.get_or_create(user=user)
    return preferences

@login_required
def index(request):
    # Get or create demo user
    user = get_or_create_user()
    preferences = get_user_preferences(user)
    
    context = {
        'user': user,
        'preferences': preferences,
    }
    return render(request, "settings/base.html", context)
@login_required
def user_info(request):
    # Get or create demo user
    user = get_or_create_user()
    
    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=user)
        if form.is_valid():
            # Handle password change
            if form.cleaned_data.get('password'):
                user.password = form.cleaned_data['password']
                user.save()
            else:
                form.save()
            messages.success(request, "Your information has been updated successfully!")
            return redirect('/settings/user_info/')
    else:
        form = UserInfoForm(instance=user)

    preferences = get_user_preferences(user)
    context = {
        'form': form, 
        'user': user,
        'preferences': preferences,
    }
    return render(request, "settings/info_user.html", context)
@login_required
def appearance(request):
    user = get_or_create_user()
    preferences = get_user_preferences(user)
    
    if request.method == 'POST':
        form = AppearanceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Appearance settings updated successfully!")
            return redirect('/settings/appearance/')
    else:
        form = AppearanceForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'user': user,
    }
    return render(request, "settings/appearance.html", context)
@login_required
def language(request):
    user = get_or_create_user()
    preferences = get_user_preferences(user)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Language settings updated successfully!")
            return redirect('/settings/language/')
    else:
        form = LanguageForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'user': user,
    }
    return render(request, "settings/language.html", context)