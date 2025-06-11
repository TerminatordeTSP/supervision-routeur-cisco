from django.apps import AppConfig # type: ignore


class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
