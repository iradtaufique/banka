from django.urls import path
from wallet import views

urlpatterns = [
    path('create/', views.WalletViewSet.as_view(), name="Create_wallet"),
    path('type/', views.WalletTypeViewSet.as_view(), name="Add_wallet_type")
]