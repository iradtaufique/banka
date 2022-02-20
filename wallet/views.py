import threading

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from authentication.models import User
from authentication.utils import Util
from wallet.serializers import WalletSerializer, TransactionSerializer, TransactionListSerializer, \
    NotificationListSerializer, NotificationUpdateSerializer, AddMoneyTransactionSerializer, \
    ListWalletInformationSerializer, ListTransactionsInformationSerializer
from .models import Wallet as WalletModel, Wallet, Transaction, TransactionType, Notification
from .payments import process_payment, process_transfer
from .permissions import IsWalletOwner
from .signals import generate_transaction_id


class TransactionsData:
    """
    add transaction data to an array to allow other method to access it
    """
    data = []
    add_data_lock = threading.Lock()

    @classmethod
    def add_data(cls, data):
        with cls.add_data_lock:
            cls.data.append(data)


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

        # Verifying if there is sufficient found in saving wallet before moving the amount to the new wallet
        if WalletModel.objects.get(user_id=user, wallet_type_id="saving").amount < float(
                self.request.data['amount']):
            raise ValidationError("Insufficient found in your saving account, please add money in it")

        # Verifying if a wallet of this type has been already created
        if WalletModel.objects.filter(user_id=user, wallet_type_id=wallet_type).exists():
            raise ValidationError("This wallet type has been already created for this user")
        wallet_data.is_valid(raise_exception=True)
        try:
            user_saving_wallet = WalletModel.objects.filter(user_id=user, wallet_type_id="saving")
            user_saving_wallet_new_amount = float(user_saving_wallet.last().amount) - float(self.request.data['amount'])
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


class AddMoneyToWalletApiView(generics.GenericAPIView):
    serializer_class = AddMoneyTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    queryset = TransactionType.objects.all()

    def post(self, request):
        serializer = AddMoneyTransactionSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']

            description = serializer.validated_data['description']

            # Verifying if there is no pending transaction before processing another one
            transaction_data_array = TransactionsData.data
            user_pending_transactions = []

            print(transaction_data_array)
            for dic in transaction_data_array:
                if dic.get('user') == self.request.user and dic.get('status') == 'pending':
                    user_pending_transactions.append(dic)

            # If there is pending transactions, we will cancel them before processing another one
            if len(user_pending_transactions) >= 1:
                print(transaction_data_array)
                TransactionsData.data = []

            transaction_data = {'amount': amount, 'user': self.request.user, 'status': 'pending',
                                'description': description}
            TransactionsData.add_data(transaction_data)

            print(process_payment(self.request.user.full_name, amount, request=request))
            redirect_link = process_payment(self.request.user.full_name, amount, request=request)

            return redirect(redirect_link)

        return Response(serializer.errors)


@require_http_methods(['GET', 'POST'])
def payment_response(request):
    status = request.GET.get('status', None)
    tx_ref = request.GET.get('tx_ref', None)

    print(status)
    print(tx_ref)
    if status == "successful":
        transaction_data_array = TransactionsData.data
        print('data: ', transaction_data_array)
        for dic in transaction_data_array:
            if dic.get('user') == request.user and dic.get('status') == 'pending':
                # getting user saving wallet
                user_saving_wallet = Wallet.objects.filter(user_id=request.user).get(wallet_type_id='SAVING')
                saving_object = Wallet.objects.filter(user_id=request.user).filter(wallet_type_id='SAVING')

                # getting the amount to add on
                amount = dic.get('amount')
                current_amount = user_saving_wallet.amount
                new_amount = current_amount + amount
                saving_object.update(amount=new_amount)
                dic['status'] = 'completed'
                notification_message = "You received money from an external source"
                receive_transaction_type = TransactionType.objects.get(transaction_type="receive")

                # saving the new transaction and a notification in database
                Transaction(to=user_saving_wallet,
                            wallet_id=user_saving_wallet,
                            description=dic.get('description'),
                            amount=amount,
                            transaction_type_id=receive_transaction_type).save()
                Util.save_notification(user=request.user, amount=amount, content=notification_message,
                                       transaction_from=request.user)
                print(dic)
                break
        return HttpResponse('Transaction succeed')

    elif status == 'cancelled':
        return HttpResponse('<h1>Transaction Failed!! </h1>')

    else:
        return HttpResponse("Transaction failed")


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

        # Getting data
        serializer = self.serializer_class(data=transaction)
        serializer.is_valid(raise_exception=True)
        send_to = transaction['to']
        print('userid: ', user)
        print('receiver id: ', send_to)
        receiver_wallet = WalletModel.objects.get(user_id=send_to, wallet_type_id="saving")
        sender_wallet = WalletModel.objects.get(user_id=user, wallet_type_id="saving")
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
        WalletModel.objects.filter(user_id=user, wallet_type_id="saving").update(amount=sender_new_founds)

        # adding money to the receiver account
        receiver_founds = receiver_wallet.amount
        receiver_new_founds = receiver_founds + sending_amount
        WalletModel.objects.filter(user_id=send_to, wallet_type_id="saving").update(amount=receiver_new_founds)

        # Retrieving transaction type into database
        transaction_send_type = TransactionType.objects.get(transaction_type="send")

        # Adding a notification to user
        receiver_user = User.objects.get(pk=send_to)
        Util.save_notification(receiver_user, sending_amount, "You've received money", user)

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

        user_wallet = WalletModel.objects.get(user_id=user.pk, wallet_type_id="saving")
        queryset = Transaction.objects.filter(wallet_id=user_wallet)
        serializer = TransactionListSerializer(queryset, many=True)
        return Response(serializer.data)


class ListUserNotificationAPIView(generics.ListAPIView):
    """
    List all new notification of logged-in user
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationListSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        notifications = Notification.objects.filter(user=user, sent=False)
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data)


class UpdateNotificationAPIView(generics.RetrieveUpdateAPIView):
    """
    When all new notifications have been retrieve and showed to user,
    this class should be called to update notification status.
    It's interesting to do it using AJAX
    so that user can use the app without interruption
    user must be authenticated
    this requires the pk of the notification.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationUpdateSerializer

    def perform_update(self, serializer):
        try:
            return serializer.save(sent=True)
        except ValueError:
            raise ValidationError("error: " + ValueError.__str__())


class AddMoneyToSchoolWallet(generics.GenericAPIView):
    """API View for adding money to School wallets"""
    serializer_class = AddMoneyTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    queryset = TransactionType.objects.all()

    def post(self, request):
        serializer = AddMoneyTransactionSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            description = serializer.validated_data['description']
            current_saving_amount = Wallet.objects.get(user_id=self.request.user, wallet_type_id='SAVING').amount
            current_saving_wallet = Wallet.objects.get(user_id=self.request.user, wallet_type_id='SAVING')
            current_school_wallet = Wallet.objects.get(user_id=self.request.user, wallet_type_id='SCHOOL')
            current_school_amount = Wallet.objects.get(user_id=self.request.user, wallet_type_id='SCHOOL').amount
            current_saving_object_amount = Wallet.objects.filter(user_id=self.request.user, wallet_type_id='SAVING')
            current_school_object_amount = Wallet.objects.filter(user_id=self.request.user, wallet_type_id='SCHOOL')

            # create transactions
            last_transaction = Transaction.objects.last().pk
            print(generate_transaction_id(last_transaction))
            Transaction.objects.create(
                wallet_id=current_saving_wallet, transaction_type_id='Saving', to=current_school_wallet,
                description=description, amount=amount, transaction_id=generate_transaction_id(last_transaction)
            )

            """check to see if amount to send is less than current amount in saving"""
            if amount <= current_saving_amount:
                new_saving_amount = current_saving_amount - amount
                new_school_amount = current_school_amount + amount
                current_school_object_amount.update(amount=new_school_amount)
                current_saving_object_amount.update(amount=new_saving_amount)
            else:
                return Response('Insufficient Amount!! Make sure you Have enaught Amount on Your Saving Account')

        return Response(serializer.data)


class AddMoneyToHouseHoldWalletAPIView(generics.GenericAPIView):
    """API View for adding money to hausehold wallets"""
    serializer_class = AddMoneyTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]
    queryset = TransactionType.objects.all()

    def post(self, request):
        serializer = AddMoneyTransactionSerializer(data=self.request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            description = serializer.validated_data['description']
            current_saving_amount = Wallet.objects.get(user_id=self.request.user, wallet_type_id='SAVING').amount
            current_saving_wallet = Wallet.objects.get(user_id=self.request.user, wallet_type_id='SAVING')
            current_household_wallet = Wallet.objects.get(user_id=self.request.user, wallet_type_id='HAUSEHOLD')
            current_hausehold_amount = Wallet.objects.get(user_id=self.request.user, wallet_type_id='HAUSEHOLD').amount
            current_saving_object_amount = Wallet.objects.filter(user_id=self.request.user, wallet_type_id='SAVING')
            current_hausehold_object_amount = Wallet.objects.filter(user_id=self.request.user,
                                                                    wallet_type_id='HAUSEHOLD')

            # create transactions
            Transaction.objects.create(
                wallet_id=current_saving_wallet, transaction_type_id='Saving', to=current_household_wallet,
                description=description, amount=amount
            )

            """check to see if amount to send is less than current amount in saving"""
            if amount <= current_saving_amount:
                new_saving_amount = current_saving_amount - amount
                new_hausehold_amount = current_hausehold_amount + amount
                current_hausehold_object_amount.update(amount=new_hausehold_amount)
                current_saving_object_amount.update(amount=new_saving_amount)
            else:
                return Response('Insufficient Amount!! Make sure you Have enought Amount on Your Saving Account')

        return Response(serializer.data)


def transfer_view(request):
    amount = 1000
    response = process_transfer(amount)
    if response['data']:
        return HttpResponse('Transaction succeed')
    return HttpResponse('Transaction failed')


class SavingWalletInformation(generics.ListAPIView):
    """API View for displaying saving wallet information"""
    serializer_class = ListWalletInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user_id=self.request.user, wallet_type_id='SAVING')


class SchoolWalletInformation(generics.ListAPIView):
    """API View for displaying school wallet information"""
    serializer_class = ListWalletInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user_id=self.request.user, wallet_type_id='SCHOOL')


class HouseHoldWalletInformation(generics.ListAPIView):
    """API View for displaying household wallet information"""
    serializer_class = ListWalletInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user_id=self.request.user, wallet_type_id='HAUSEHOLD')


class ListUserTransactionInformation(generics.ListAPIView):
    """API View for displaying all users transactions"""
    serializer_class = ListTransactionsInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet_id__user_id=self.request.user)
