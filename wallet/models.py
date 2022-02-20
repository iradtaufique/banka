from django.contrib.auth import get_user_model
from django.db import models

from authentication.models import User

User = get_user_model()

WalletType = (
    ('SAVING', 'SAVING'),
    ('HAUSEHOLD', 'HAUSEHOULD'),
    ('SCHOOL', 'SCHOOL'),
)


class Wallet(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    wallet_type_id = models.CharField(max_length=30, choices=WalletType)
    wallet_number = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.user_id} {self.wallet_type_id}'


class Transaction(models.Model):
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type_id = models.CharField(max_length=40)
    date = models.DateField(auto_now=True)
    to = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="send_to", verbose_name='Send to')
    description = models.TextField()
    amount = models.FloatField(blank=False, null=False)
    transaction_id = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return f'{self.wallet_id}'


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
