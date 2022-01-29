from django.db import models
from django.contrib.auth import get_user_model
from authentication.models import User

# User = get_user_model()


class WalletType(models.Model):
    wallet_type = models.CharField(max_length=30)

    def __str__(self):
        return self.wallet_type


class Wallet(models.Model):
    # user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    wallet_type_id = models.ForeignKey(WalletType, on_delete=models.CASCADE)

    # def __str__(self):
    #     return str(self.user_id) + ' ' + str(self.amount)


class TransactionType(models.Model):
    transaction_type = models.CharField(max_length=30)

    def __str__(self):
        return self.transaction_type


class Transaction(models.Model):
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type_id = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    # to = models.ForeignKey(User, on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.wallet_id + 'to ' + self.to
