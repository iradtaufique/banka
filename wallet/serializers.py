from django.contrib.auth import get_user_model
from rest_framework import serializers

from wallet.models import Wallet, Transaction, Notification

User = get_user_model()


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for wallet
    """

    class Meta:
        model = Wallet
        fields = ['wallet_type_id', 'amount']

    def validate(self, data):
        if float(data['amount']) < 0:
            raise serializers.ValidationError('The amount cannot be negative')
        return data


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Transaction
    """
    to = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.filter(wallet_type_id="SAVING"))

    class Meta:
        model = Transaction
        # We will just allow sending money so no need to add transaction type into fields
        # But, we will save transaction according to user in views
        fields = ['amount', 'date', 'to', 'description']

    def validate(self, data):
        if float(data['amount']) < 0:
            raise serializers.ValidationError('The amount cannot be negative')
        return data


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
    saving_wallet = Wallet.objects.filter(wallet_type_id="SAVING")

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


class ListWalletInformationSerializer(serializers.ModelSerializer):
    """serializer for listing wallet information"""

    class Meta:
        model = Wallet
        fields = '__all__'

    def to_representation(self, instance):
        wallet_owner = super(ListWalletInformationSerializer, self).to_representation(instance)
        wallet_owner['user_id'] = instance.user_id.full_name
        return wallet_owner


class ListTransactionsInformationSerializer(serializers.ModelSerializer):
    """serializer for listing transaction information"""

    class Meta:
        model = Transaction
        fields = '__all__'
