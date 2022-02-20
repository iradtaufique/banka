"""functions for generating wallets numbers"""
from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import User
from wallet.models import Wallet, Transaction


def generate_saving_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id="SAVING").all().count()
    year = datetime.now().year
    code = 1
    if all_saving_wallet:
        code = all_saving_wallet + code
        return 'SWV-' + str(year) + '-' + str(code)


def generate_school_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id='SCHOOL').all().count()
    year = datetime.now().year
    code = 1
    if all_saving_wallet:
        code = all_saving_wallet+code
        return 'SW-' + str(year) + '-' + str(code)


def generate_hausehold_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id='HAUSEHOLD').all().count()
    year = datetime.now().year
    code = 1
    if all_saving_wallet:
        code = all_saving_wallet + code
        return 'HW-' + str(year) + '-' + str(code)


def generate_transaction_id(id):
    transactions_number = Transaction.objects.all().count()
    print("transaction number: ", transactions_number)
    year = datetime.now().year
    id = id + 1
    if transactions_number:
        return 'TRANS' + str(year) + '-' + str(transactions_number) + str(id)
    return 'TRANS' + str(year) + '-' + "0" + str(id)


""" End of functions that generate wallet id numbers"""


@receiver(post_save, sender=User)
def create_saving_wallet(sender, instance, created, **kwargs):
    """
    A saving wallet will be created automatically for every new user added in the database
    We need to save in wallet_type a 'saving' type before creating user.
    Else, the app will crash
    """
    if created:
        Wallet.objects.create(user_id=instance, wallet_type_id="SAVING", amount=0, wallet_number=generate_saving_wallet_id_number())
        Wallet.objects.create(user_id=instance, wallet_type_id='SCHOOL', amount=0, wallet_number=generate_school_wallet_id_number())
        Wallet.objects.create(user_id=instance, wallet_type_id='HAUSEHOLD', amount=0, wallet_number=generate_hausehold_wallet_id_number())
