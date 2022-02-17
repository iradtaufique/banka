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
    path('add-money/', views.AddMoneyToWalletApiView.as_view(), name='add_money')
]