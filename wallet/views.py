from rest_framework import generics
from rest_framework.response import Response

from wallet.serializers import WalletSerializer, WalletTypeSerializer

from .models import Wallet as WalletModel, WalletType


class WalletTypeViewSet(generics.GenericAPIView):
    serializer_class = WalletTypeSerializer
    queryset = WalletType.objects.all()

    def post(self, request):
        wallet_type = self.request.data
        serializer = self.serializer_class(data=wallet_type)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
