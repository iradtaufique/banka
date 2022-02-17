from django.urls import path
from wallet import views


urlpatterns = [

    path('create/', views.CreateWalletAPIView.as_view(), name="create_wallet"),
    path('type/', views.CreateWalletTypeAPIView.as_view(), name="add_wallet_type"),
    path('list/', views.ListWalletAPIView.as_view(), name="list_wallet"),
    path('send-money/', views.SendMoneyAPIView.as_view(), name="send_money"),
    path('update/<int:pk>', views.UpdateWalletAPIView.as_view(), name="update_wallet"),
    path('transactions-list/', views.ListTransactionAPIView.as_view(), name="List_of_transactions"),
    path('transfert/', views.transfer_view, name="Transfer"),
    path('callback', views.payment_response, name="payment_response"),

    # adding money to wallet
    path('add-money/', views.AddMoneyToWalletApiView.as_view(), name='add_money'),
    path('add-money-school/', views.AddMoneyToSchoolWallet.as_view(), name='add_money_to_school'),
    path('add-money-hausehold/', views.AddMoneyToHouseHoldWalletAPIView.as_view(), name='add_money_to_hausehold'),

    # urls for listing users wallets information
    path('saving-wallet-info/', views.SavingWalletInformation.as_view(), name='saving_wallet_info'),
    path('school-wallet-info/', views.SchoolWalletInformation.as_view(), name='school_wallet_info'),
    path('household-wallet-info/', views.HouseHoldWalletInformation.as_view(), name='household_wallet_info'),
    path('transaction-info/', views.ListUserTransactionInformation.as_view(), name='user_transaction_info'),
]