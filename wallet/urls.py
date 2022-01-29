from django.urls import path
from wallet import views

urlpatterns = [
    path('create/', views.CreateWalletAPIView.as_view(), name="Create_wallet"),
    path('type/', views.CreateWalletTypeAPIView.as_view(), name="Add_wallet_type"),
    path('list/', views.ListWalletAPIView.as_view(), name="List_wallet"),
    # TODO adda good url
    path('update/<int:pk>', views.UpdateWalletAPIView.as_view(), name="Update_wallet"),

]