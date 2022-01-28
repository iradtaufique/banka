from django.urls import path
from wallet import views

urlpatterns = [
    path('wallet/', views.WalletViewSet.as_view(), name="Create_wallet"),
]