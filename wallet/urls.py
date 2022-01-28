from django.urls import path
from wallet import views

urlpatterns = [
    path('type/', views.WalletTypeViewSet.as_view(), name="Add_wallet_type")
]