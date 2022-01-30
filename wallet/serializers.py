from rest_framework import serializers

from wallet.models import Wallet, WalletType, Transaction, TransactionType


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for wallet
    """
    wallet_type_id = serializers.PrimaryKeyRelatedField(queryset=WalletType.objects.all())

    class Meta:
        model = Wallet
        fields = ['wallet_type_id', 'amount']


class WalletTypeSerializer(serializers.HyperlinkedModelSerializer):
    """"
    Serializer for walletType
    """

    class Meta:
        model = WalletType
        fields = ['wallet_type']


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Transaction
    """

    class Meta:
        model = Transaction
        # We will just allow sending money so no need to add transaction type into fields
        # But, we will save transaction according to user in views
        fields = ['wallet_id', 'date', 'to']


class TransactionTypeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for transactionType
    """

    class Meta:
        model = TransactionType
        fields = ['transaction_type']
