from django.shortcuts import render, redirect
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from wallet.serializers import WalletSerializer, WalletTypeSerializer, AddMoneyToWalletSerializer

from .models import Wallet as WalletModel, WalletType, Wallet
from django.db.models.signals import post_save, pre_save

from .payments import process_payment
from .permissions import IsWalletOwner
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

User = get_user_model()


class CreateWalletAPIView(generics.GenericAPIView):
    """
    Class to create a wallet
    user must be authenticated
    """
    # Users must be authenticated before accessing any method in this class
    # permissions_classes = permissions.IsAuthenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer
    queryset = WalletModel.objects.all()

    def post(self, request):
        wallet = self.request.data
        wallet_data = self.serializer_class(data=wallet)
        user = self.request.user
        wallet_type = self.request.data['wallet_type_id']
        if WalletModel.objects.filter(user_id=user, wallet_type_id=wallet_type).exists():
            raise ValidationError("This wallet type has been already created for this user")
        wallet_data.is_valid(raise_exception=True)
        wallet_data.save(user_id=user)

        return Response(wallet_data.data)


class UpdateWalletAPIView(generics.RetrieveUpdateAPIView):
    """
    Update wallet
    user must be authenticated
    All fields must be submitted
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    queryset = WalletModel.objects.all()

    def perform_update(self, serializer):
        return serializer.save(user_id=self.request.user)

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


# @receiver(post_save, sender=User)
# def create_saving_wallet(sender, instance, **kwargs):
#     """
#     A saving wallet will be create automatically for every new user added in the database
#     """
#     try:
#         # TODO ensure that saving wallet_type has been added to the database with the same name
#         # wallet type that will be created first is the saving one
#         wallet_type = WalletType.objects.filter(wallet_type="saving").last()
#         new_wallet = Wallet(user_id=instance, wallet_type_id=wallet_type, amount=0)
#         new_wallet.save()
#     except:
#         # TODO solve why a new saving wallet want to be created when user is updated
#         raise ValidationError("Unable to create a saving wallet")



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