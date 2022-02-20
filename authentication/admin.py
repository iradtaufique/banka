from django.contrib import admin
from authentication.models import User
from wallet.models import Wallet, Transaction, Notification

admin.site.register(User)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Notification)
