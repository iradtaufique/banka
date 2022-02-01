from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.db.models.signals import post_save, pre_save

from .payments import process_payment

from authentication.models import User
from wallet.serializers import WalletSerializer, WalletTypeSerializer, TransactionSerializer, TransactionListSerializer, AddMoneyToWalletSerializer
from .models import Wallet as WalletModel, WalletType, Wallet, Transaction, TransactionType
from .permissions import IsWalletOwner
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse




class CreateWalletAPIView(generics.GenericAPIView):
    """
    Class to create a wallet
    user must be authenticated
    He will send money from his saving account to the new one
    He should have sufficient founds in this account thus
    """
    # Users must be authenticated before accessing any method in this class
    # permissions_classes = permissions.IsAuthenticated
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    serializer_class = WalletSerializer
    queryset = WalletModel.objects.all()

    def post(self, request):
        wallet = self.request.data
        wallet_data = self.serializer_class(data=wallet)
        user = self.request.user
        wallet_type = self.request.data['wallet_type_id']

        # Retrieving saving wallet type
        saving_wallet = WalletType.objects.get(wallet_type='saving')

        # Verifying if there is sufficient found in saving wallet before moving the amount to the new wallet
        if WalletModel.objects.get(user_id=user, wallet_type_id=saving_wallet.pk).amount < float(
                self.request.data['amount']):
            raise ValidationError("Insufficient found in your saving account, please add money in it")

        # Verifying if a wallet of this type has been already created
        if WalletModel.objects.filter(user_id=user, wallet_type_id=wallet_type).exists():
            raise ValidationError("This wallet type has been already created for this user")
        wallet_data.is_valid(raise_exception=True)
        try:
            user_saving_wallet = WalletModel.objects.filter(user_id=user, wallet_type_id=saving_wallet.pk)
            user_saving_wallet_new_amount = float(user_saving_wallet.last().amount)-float(self.request.data['amount'])
            user_saving_wallet.update(amount=user_saving_wallet_new_amount)
            wallet_data.save(user_id=user)
        except ValueError:
            raise ValidationError("An error occurred while saving data: " + ValueError.__str__())

        return Response(wallet_data.data)


class UpdateWalletAPIView(generics.RetrieveUpdateAPIView):
    """
    Update wallet
    User must be authenticated
    All fields must be submitted
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    queryset = WalletModel.objects.all()

    def perform_update(self, serializer):
        try:
            return serializer.save(user_id=self.request.user)
        except ValueError:
            raise ValidationError("error: " + ValueError.__str__())


class ListWalletAPIView(generics.ListAPIView):
    """
    List wallet for authenticated user,
    He must be authenticated and owner of the wallet
    """
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    serializer_class = WalletSerializer
    queryset = WalletModel.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        queryset = WalletModel.objects.filter(user_id=user)
        serializer = WalletSerializer(queryset, many=True)
        return Response(serializer.data)


class CreateWalletTypeAPIView(generics.GenericAPIView):
    """
    class to create wallet type,
    In case a user want to create another wallet type
    Different from existent wallet type
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletTypeSerializer
    queryset = WalletType.objects.all()

    def post(self, request):
        wallet_type = self.request.data
        serializer = self.serializer_class(data=wallet_type)

        # checking if user new wallet type does not exist in database
        user_wallet_type = wallet_type['wallet_type']
        if WalletType.objects.filter(wallet_type=user_wallet_type).exists():
            raise ValidationError("This wallet type already exists, go ahead and create your wallet directly please")

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AddMoneyToWalletApiView(APIView):
    serializer_class = AddMoneyToWalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]

    def post(self, request):
        serializer = AddMoneyToWalletSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            name = serializer.validated_data['names']

            """getting saving wallet from walletType"""
            saving_wallet = WalletType.objects.get(wallet_type='saving')
            """get user saving wallet"""
            user_saving_wallet = Wallet.objects.filter(user_id=request.user).get(wallet_type_id=saving_wallet)
            saving_object = Wallet.objects.filter(user_id=request.user).filter(wallet_type_id=saving_wallet)
            current_amount = user_saving_wallet.amount
            new_amount = current_amount + amount
            saving_object.update(amount=new_amount)

            serializer.save()
            print(process_payment(name, amount))
            redirect_link = process_payment(name, amount)
            return redirect(redirect_link)

        return Response(serializer.errors)


@require_http_methods(['GET', 'POST'])
def payment_response(request):
    status=request.GET.get('status', None)
    tx_ref=request.GET.get('tx_ref', None)
    amount=request.GET.get('amount', None)
    currency=request.GET.get('currency', None)

    print(status)
    print(tx_ref)

    return HttpResponse('Finished')


class SendMoneyAPIView(generics.GenericAPIView):
    """
    Class for sending money to another user into the system
    The sender must be authenticated and the owner of the wallet he use
    He should have enough money in the account he'll use to send money.
    """
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def post(self, request):
        transaction = self.request.data
        user = self.request.user
        # Retrieving saving wallet type
        saving_wallet = WalletType.objects.get(wallet_type='saving')

        # Getting data
        sender_wallet = WalletModel.objects.get(user_id=user, wallet_type_id=saving_wallet.pk)
        serializer = self.serializer_class(data=transaction)
        serializer.is_valid(raise_exception=True)
        send_to = transaction['to']
        receiver_wallet = WalletModel.objects.get(user_id=send_to, wallet_type_id=saving_wallet.pk)
        sending_amount = float(transaction['amount'])

        # Verifying if the sender has sufficient found
        if sender_wallet.amount < sending_amount:
            raise ValidationError("Insufficient founds. Please charge your account and try again.")

        # Verifying if user sends money to his account
        if receiver_wallet.user_id == user:
            raise ValidationError("Cannot send money to your account. To send to one of your wallets, please refer to "
                                  "the good link")

        # removing money from the sender account
        sender_founds = sender_wallet.amount.__float__()
        sender_new_founds = sender_founds - sending_amount
        WalletModel.objects.filter(user_id=user, wallet_type_id=1).update(amount=sender_new_founds)

        # adding money to the receiver account
        receiver_founds = receiver_wallet.amount
        receiver_new_founds = receiver_founds + sending_amount
        WalletModel.objects.filter(user_id=send_to, wallet_type_id=saving_wallet.pk).update(amount=receiver_new_founds)

        # Retrieving transaction type into database
        transaction_send_type = TransactionType.objects.get(transaction_type="send")

        # saving transaction
        serializer.save(wallet_id=sender_wallet, transaction_type_id=transaction_send_type, to=receiver_wallet)

        return Response(serializer.data)


class ListTransactionAPIView(generics.ListAPIView):
    """
    List transactions for authenticated user,
    He must be authenticated and the owner of the wallet wallet_id
    wallet_id represents the sender and to represents the receiver, transaction_type_id represents the type of transaction done
    """
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    serializer_class = TransactionListSerializer
    queryset = Transaction.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        # Retrieving saving wallet type
        saving_wallet = WalletType.objects.get(wallet_type='saving')

        user_wallet = WalletModel.objects.get(user_id=user.pk, wallet_type_id=saving_wallet.pk)
        queryset = Transaction.objects.filter(wallet_id=user_wallet)
        serializer = TransactionListSerializer(queryset, many=True)
        return Response(serializer.data)


@receiver(post_save, sender=User)
def create_saving_wallet(sender, instance, **kwargs):
    """
    A saving wallet will be created automatically for every new user added in the database
    We need to save in wallet_type a 'saving' type before creating user.
    Else, the app will crash
    """
    try:
        # wallet type that will be created first is the saving one
        wallet_type = WalletType.objects.get(wallet_type="saving")
        print('instance: ', instance)

        # Verifying if the user is authenticated before saving
        if instance:
            wallet_exists = Wallet.objects.filter(user_id=instance, wallet_type_id=wallet_type)
            new_wallet = Wallet(user_id=instance, wallet_type_id=wallet_type, amount=0)

            if wallet_exists:
                wallet_exists.update(user_id=instance, wallet_type_id=wallet_type, amount=0)
            else:
                new_wallet.save()
    except:
        raise ValidationError("Unable to create a saving wallet")

