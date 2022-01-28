from rest_framework import generics
from rest_framework.response import Response

from wallet.serializers import WalletSerializer

from .models import Wallet as WalletModel


class WalletViewSet(generics.ListAPIView):
    """
    Class to handle every interaction with wallet
    CRUD wallet
    """
    # Users must be authenticated before accessing any method in this class
    # permissions_classes = permissions.IsAuthenticatedOrReadOnly
    serializer_class = WalletSerializer
    queryset = WalletModel.objects.all()

    """def create_wallet(self):
        self.post()
        return Response(wallet_data)"""

    def post(self, request):
        wallet = self.request.data
        wallet_data = self.serializer_class(data=wallet)
        user = self.request.user
        # wallet_type = self.request.data['wallet_type']
        wallet_data.is_valid(raise_exception=True)
        wallet_data.save(user_id=user)
        return Response(wallet_data)