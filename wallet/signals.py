"""functions for generating wallets numbers"""
from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import User
from wallet.models import Wallet, Transaction


def generate_saving_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id="SAVING").all().count()
    year = datetime.now().year
    wallet = Wallet.objects.last()
    code = 0
    if wallet:
        code = wallet.pk + 1
    if all_saving_wallet:
        return 'SWV-' + str(year) + '-' + str(all_saving_wallet) + str(code)
    return 'SWV-' + str(year) + '-' + '0' + str(code)


def generate_school_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id='SCHOOL').all().count()
    year = datetime.now().year
    wallet = Wallet.objects.last()
    code = 0
    if wallet:
        code = wallet.pk + 1
    if all_saving_wallet:
        return 'SW-' + str(year) + '-' + str(all_saving_wallet) + str(code)
    return 'SW-' + str(year) + '-' + '0' + str(code)


def generate_hausehold_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id='HAUSEHOLD').all().count()
    wallet = Wallet.objects.last()
    year = datetime.now().year
    # If there were some wallet in database, the new one will have number composed of the pk of the last + 1 else its
    # number will be composed of 0
    code = 0
    if wallet:
        code = wallet.pk + 1
    if all_saving_wallet:
        return 'HW-' + str(year) + '-' + str(all_saving_wallet) + str(code)
    return 'HW-' + str(year) + '-' + '0' + str(code)


def generate_transaction_id():
    last_transaction = Transaction.objects.last()
    id = 0
    if last_transaction:
        id = last_transaction.pk + 1
    transactions_number = Transaction.objects.all().count()
    print("transaction number: ", transactions_number)
    year = datetime.now().year
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
