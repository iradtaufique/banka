from django.contrib import admin
from authentication.models import User
from wallet.models import WalletType

admin.site.register(User)
admin.site.register(WalletType)
