from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class WalletType(models.Model):
    wallet_type = models.CharField(max_length=30)


class Wallet(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    wallet_type_id = models.ForeignKey(WalletType, on_delete=models.CASCADE)


class TransactionType(models.Model):
    transaction_type = models.CharField(max_length=30)


class Transaction(models.Model):
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type_id = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    to = models.ForeignKey(User, on_delete=models.CASCADE)

