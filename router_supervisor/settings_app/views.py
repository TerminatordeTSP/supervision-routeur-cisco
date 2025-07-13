from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from router_supervisor.core_models.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from router_supervisor.settings_app.forms import CustomUserCreationForm

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
