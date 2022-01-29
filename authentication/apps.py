from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'


from django.apps import AppConfig
from django.core.signals import request_finished


class MyAppConfig(AppConfig):

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from wallet import views
        # Explicitly connect a signal handler.
        request_finished.connect(views.create_saving_wallet, dispatch_uid="azerty123")
