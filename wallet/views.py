from django.contrib.auth import get_user_model
from django.dispatch import receiver
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from wallet.serializers import WalletSerializer, WalletTypeSerializer, TransactionSerializer

from .models import Wallet as WalletModel, WalletType, Wallet, Transaction, TransactionType
from django.db.models.signals import post_save, pre_save

User = get_user_model()


class CreateWalletAPIView(generics.GenericAPIView):
    """
    Class to create a wallet
    user must be authenticated
    He will send money from his saving account to the new one
    He should have sufficient founds in this account thus
    """
    # Users must be authenticated before accessing any method in this class
    permissions_classes = permissions.IsAuthenticated
    serializer_class = WalletSerializer
    queryset = WalletModel.objects.all()

    def post(self, request):
        wallet = self.request.data
        wallet_data = self.serializer_class(data=wallet)
        user = self.request.user
        wallet_type = self.request.data['wallet_type_id']
        # TODO add a verification of founds in the saving wallet and subtract money in this wallet to add to the
        #  other one
        if WalletModel.objects.filter(user_id=user, wallet_type_id=wallet_type).exists():
            raise ValidationError("This wallet type has been already created for this user")
        wallet_data.is_valid(raise_exception=True)
        wallet_data.save(user_id=user)

        return Response(wallet_data.data)


class UpdateWalletAPIView(generics.GenericAPIView, UpdateModelMixin):
    """
    Update wallet
    user must be authenticated
    All fields must be submitted
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WalletModel.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)



class ListWalletAPIView(generics.ListAPIView):
    """
    List wallet for authenticated user
    he must be authenticated
    """
    permission_classes = [permissions.IsAuthenticated]
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
    in case a user want to create another wallet type
    different from existent wallet type
    """
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


@receiver(post_save, sender=User)
def create_saving_wallet(sender, instance, **kwargs):
    """
    A saving wallet will be create automatically for every new user added in the database
    """
    try:
        # TODO ensure that saving wallet_type has been added to the database with the same name
        # wallet type that will be created first is the saving one
        wallet_type = WalletType.objects.filter(wallet_type="saving").last()
        new_wallet = Wallet(user_id=instance, wallet_type_id=wallet_type, amount=0)
        new_wallet.save()
    except:
        # TODO solve why a new saving wallet want to be created when user is updated
        raise ValidationError("Unable to create a saving wallet")


class SendMoneyAPIView(generics.GenericAPIView):
    """
    Class for sending money to another user into the system
    The sender must be authenticated and the owner of the wallet he use
    He should have enough money in the account he'll use to send money.
    """
    # permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def post(self, request):
        transaction = self.request.data
        user = self.request.user
        sender_wallet = WalletModel.objects.filter(user_id=user).last()
        serializer = self.serializer_class(data=transaction)
        serializer.is_valid(raise_exception=True)
        send_to = transaction['to']
        sending_amount = transaction['amount']

        # removing money from the sender account
        sender_founds = sender_wallet.amount
        sender_new_founds = sender_founds - sending_amount
        sender_wallet.update(amount=sender_new_founds)

        # adding money to the receiver account
        receiver_wallet = WalletModel.objects.filter(user_id=send_to).last()
        receiver_founds = receiver_wallet.amount
        receiver_new_founds = receiver_founds + sending_amount
        receiver_wallet.update(amount=receiver_new_founds)

        # Retrieving transaction type into database
        transaction_send_type = TransactionType.objects.filter(transaction_type="send")

        # saving transaction
        serializer.save(wallet_id=sender_wallet, transaction_type=transaction_send_type, to=receiver_wallet)
        # TODO do we really need transaction type model ? Because we are just allowing sending transaction or should
        #  we include receiving transaction also ?


