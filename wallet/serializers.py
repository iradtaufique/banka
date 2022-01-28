from rest_framework import serializers

from wallet.models import Wallet, WalletType, Transaction, TransactionType


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for wallet
    """
    # wallet_type_id = serializers.ChoiceField()

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
        fields = ['transaction_type_id', 'wallet_id', 'date', 'to']


class TransactionTypeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for transactionType
    """

    class Meta:
        model = TransactionType
        fields = ['transaction_type']
