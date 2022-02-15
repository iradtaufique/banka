from datetime import datetime

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


WALLET_TYPE = (
    ('SAVING', 'SAVING'),
    ('HAUSEHOLD', 'HAUSEHOLD'),
    ('SCHOOL', 'SCHOOL'),
)


def generate_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id='SAVING').all().count()
    all_hausehold_wallet = Wallet.objects.filter(wallet_type_id='HAUSEHOLD').all().count()
    all_school_wallet = Wallet.objects.filter(wallet_type_id='SCHOOL').all().count()
    year = datetime.now().year

    code = 1
    if not all_saving_wallet:
        return 'SV-' + str(year) + '-' + str(code)

    elif all_saving_wallet:
        code = code + all_saving_wallet
        return 'SV-' + str(year) + '-' + str(code)


class Wallet(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    # wallet_type_id = models.ForeignKey(WalletType, on_delete=models.CASCADE)
    wallet_type_id = models.CharField(max_length=30, choices=WALLET_TYPE)
    wallet_number = models.CharField(max_length=30, default=generate_wallet_id_number)


    def __str__(self):
        return f'{self.user_id} {self.wallet_type_id}'




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
    sent = models.BooleanField(default=False)
    transaction_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_from")
    received_amount = models.FloatField()
