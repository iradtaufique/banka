from django.urls import path
from wallet import views
from wallet.views import AddMoneyToWalletApiView

urlpatterns = [
    path('create/', views.CreateWalletAPIView.as_view(), name="Create_wallet"),
    path('type/', views.CreateWalletTypeAPIView.as_view(), name="Add_wallet_type"),
    path('list/', views.ListWalletAPIView.as_view(), name="List_wallet"),
    path('update/<int:pk>', views.UpdateWalletAPIView.as_view(), name="Update_wallet"),
    path('callback', views.payment_response, name="payment_response"),

    # adding money to wallet
    path('add-money/', views.AddMoneyToWalletApiView.as_view(), name='add_money')
]