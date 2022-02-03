from django.contrib.auth import get_user_model
from rest_framework import serializers

from authentication.utils import Util
from wallet.models import AddMoneyToWallet
from wallet.models import Wallet, WalletType, Transaction, TransactionType, Notification

User = get_user_model()


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for wallet
    """
    wallet_type_id = serializers.PrimaryKeyRelatedField(queryset=WalletType.objects.all())

    class Meta:
        model = Wallet
        fields = ['wallet_type_id', 'amount']

    def validate(self, data):
        if float(data['amount']) < 0:
            raise serializers.ValidationError('The amount cannot be negative')
        return data


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
    # Before accessing WalletType model here, we need to check if its table exists to avoid having exceptions
    table_name = "wallet_wallettype"
    if Util.db_table_exists(table_name):
        if WalletType.objects.filter(wallet_type="saving").exists():
            saving_wallet = WalletType.objects.get(wallet_type="saving")
            to = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter(wallet_type_id=saving_wallet))

    class Meta:
        model = Transaction
        # We will just allow sending money so no need to add transaction type into fields
        # But, we will save transaction according to user in views
        fields = ['amount', 'date', 'to', 'description']

    def validate(self, data):
        if float(data['amount']) < 0:
            raise serializers.ValidationError('The amount cannot be negative')
        return data


class TransactionTypeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for transactionType
    """

    class Meta:
        model = TransactionType
        fields = ['transaction_type']


class AddMoneyToWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddMoneyToWallet
        fields = ['amount', 'description']


class TransactionListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Transaction List only
    """
    to = serializers.CharField(source='to.user_id')
    wallet_id = serializers.CharField(source='wallet_id.user_id')
    transaction_type_id = serializers.CharField(source='transaction_type_id.transaction_type')

    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'wallet_id', 'to', 'transaction_type_id']


class NotificationListSerializer(serializers.HyperlinkedModelSerializer):
    transaction_from = serializers.CharField(source='transaction_from.email')

    class Meta:
        model = Notification
        fields = ['created', 'content', 'transaction_from', 'received_amount', 'pk']


class NotificationUpdateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notification
        fields = []


class AddMoneyTransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Transaction
    """
    # Before accessing WalletType model here, we need to check if its table exists to avoid having exceptions
    table_name = "wallet_wallettype"
    if Util.db_table_exists(table_name):
        if WalletType.objects.filter(wallet_type="saving").exists():
            saving_wallet = WalletType.objects.get(wallet_type="saving")
            # to = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter(wallet_type_id=saving_wallet))

    class Meta:
        model = Transaction
        # We will just allow sending money so no need to add transaction type into fields
        # But, we will save transaction according to user in views
        fields = ['amount', 'description']

    def validate(self, data):
        if float(data['amount']) < 0:
            raise serializers.ValidationError('The amount cannot be negative')
        return data
