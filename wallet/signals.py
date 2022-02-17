"""functions for generating wallets numbers"""
from rest_framework.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import User
from wallet.models import Wallet, WalletType, Transaction
from datetime import datetime


def generate_saving_wallet_id_number():
    all_saving_wallet = Wallet.objects.filter(wallet_type_id='SAVING').all().count()
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


""" End of functions that generate wallet id numbers"""


# @receiver(post_save, sender=User)
# def create_saving_wallet(sender, instance, created, **kwargs):
#     """
#     A saving wallet will be created automatically for every new user added in the database
#     We need to save in wallet_type a 'saving' type before creating user.
#     Else, the app will crash
#     """
#     if created:
#         try:
#             # wallet type that will be created first is the saving one
#             wallet_type = WalletType.objects.get(wallet_type="saving")
#
#             # Verifying if the user is authenticated before saving
#             if instance:
#                 wallet_exists = Wallet.objects.filter(user_id=instance, wallet_type_id='SAVING')
#                 new_wallet = Wallet(user_id=instance, wallet_type_id='SAVING', amount=0, wallet_number=generate_saving_wallet_id_number())
#                 Wallet.objects.create(user_id=instance, wallet_type_id='SCHOOL', amount=0, wallet_number=generate_school_wallet_id_number())
#                 Wallet.objects.create(user_id=instance, wallet_type_id='HAUSEHOLD', amount=0, wallet_number=generate_hausehold_wallet_id_number())
#
#                 if wallet_exists:
#                     wallet_exists.update(user_id=instance, wallet_type_id='SAVING', amount=0, wallet_number=generate_saving_wallet_id_number())
#                 else:
#                     new_wallet.save()
#         except:
#             raise ValidationError("Unable to create a saving wallet")


@receiver(post_save, sender=User)
def create_saving_wallet(sender, instance, created, **kwargs):
    """
    A saving wallet will be created automatically for every new user added in the database
    We need to save in wallet_type a 'saving' type before creating user.
    Else, the app will crash
    """
    if created:
        Wallet.objects.create(user_id=instance, wallet_type_id='SAVING', amount=0, wallet_number=generate_saving_wallet_id_number())
        Wallet.objects.create(user_id=instance, wallet_type_id='SCHOOL', amount=0, wallet_number=generate_school_wallet_id_number())
        Wallet.objects.create(user_id=instance, wallet_type_id='HAUSEHOLD', amount=0, wallet_number=generate_hausehold_wallet_id_number())



@receiver(post_save, sender=Wallet)
def create_transactions(sender, instance, created, **kwargs):
    """
    A saving wallet will be created automatically for every new user added in the database
    We need to save in wallet_type a 'saving' type before creating user.
    Else, the app will crash
    """
    if created:
        Transaction.objects.create(wallet_id=instance, transaction_type_id='Send', )

