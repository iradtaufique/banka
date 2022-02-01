from django.contrib import admin
from authentication.models import User
from wallet.models import WalletType, Wallet, Transaction, TransactionType, Notification

admin.site.register(User)
admin.site.register(WalletType)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(TransactionType)
admin.site.register(Notification)
