from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    verbose_name = 'Users'

    def ready(self):
        from .updater import updater
        updater.start()
