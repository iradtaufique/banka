from django.apps import AppConfig


class WalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wallet'

    """registering file which contains signals snippets"""
    def ready(self):
        import wallet.signals
