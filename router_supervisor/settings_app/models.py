from django.db import models
from django.conf import settings


class UserPreferences(models.Model):
    """Modèle pour les préférences utilisateur"""
    
    THEME_CHOICES = [
        ('orange', 'Orange Theme'),
        ('blue', 'Blue Theme'),
        ('green', 'Green Theme'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='orange'
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
