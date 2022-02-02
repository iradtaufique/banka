from django.db import models
from django.contrib.auth import get_user_model
from authentication.models import User

User = get_user_model()


class WalletType(models.Model):
    wallet_type = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.wallet_type + ' ' + self.id.__str__()

    def validate_unique(self, exclude=None):
        if not self.wallet_type.isalpha():
            raise ValueError("wallet type should be a alpha type")


class Wallet(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    wallet_type_id = models.ForeignKey(WalletType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user_id', 'wallet_type_id']

    def __str__(self):
        user = User.objects.get(email=self.user_id)
        wallet_type = WalletType.objects.get(pk=self.wallet_type_id.pk)
        return user.__str__()

    def validate_unique(self, exclude=None):
        if self.amount < 0:
            raise ValueError("The amount cannot be bellow zero")



class TransactionType(models.Model):
    transaction_type = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.transaction_type

    def validate_unique(self, exclude=None):
        if not self.transaction_type.isalpha():
            raise ValueError("transaction type should be a alpha type")


class Transaction(models.Model):
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type_id = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    to = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="send_to", verbose_name='Send to')
    description = models.TextField()
    amount = models.FloatField(blank=False, null=False)

    def __str__(self):
        sender_email = self.wallet_id.user_id
        send_from = User.objects.get(email=sender_email)
        send_to = User.objects.get(email=self.to.user_id)
        return 'from: ' + str(send_from) + 'to ' + str(send_to) + ' Type: ' + self.transaction_type_id.transaction_type

    def validate_unique(self, exclude=None):
        if self.amount < 0:
            raise ValueError("The amount cannot be bellow zero")


class Notification(models.Model):
    """
    this class will contain all notification that we need,
    we will connect it to our users so that every user get their notification when they connect
    """
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(null=True, blank=True)
    transaction_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_from")
    received_amount = models.FloatField()


class AddMoneyToWallet(models.Model):
    names = models.CharField(max_length=30)
    amount = models.IntegerField()

