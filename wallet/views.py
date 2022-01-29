from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from wallet.serializers import WalletSerializer, WalletTypeSerializer

from .models import Wallet as WalletModel, WalletType


class WalletViewSet(generics.GenericAPIView):
    """
    Class to handle every interaction with wallet
    CRUD wallet
    """
    # Users must be authenticated before accessing any method in this class
    permissions_classes = permissions.IsAuthenticated
    serializer_class = WalletSerializer
    queryset = WalletModel.objects.all()

    def post(self, request):
        wallet = self.request.data
        wallet_data = self.serializer_class(data=wallet)
        user = self.request.user
        wallet_type = self.request.data['wallet_type']
        if WalletModel.objects.filter(user_id=user, wallet_type_id=wallet_type).exists():
            raise ValidationError("This wallet type has been already created for this user")
        wallet_data.is_valid(raise_exception=True)
        wallet_data.save(user_id=user)

        return Response(wallet_data.data)

        # return serializer(user_id=self.request.user)


class WalletTypeViewSet(generics.GenericAPIView):
    serializer_class = WalletTypeSerializer
    queryset = WalletType.objects.all()

    def post(self, request):
        wallet_type = self.request.data
        serializer = self.serializer_class(data=wallet_type)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)