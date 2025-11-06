from django.urls import path

from terminal.apps import TerminalConfig
from . import views

app_name = TerminalConfig.name

urlpatterns = [
    path('wallets/', views.ListWalletView.as_view(), name='wallet_list'),
    path('wallets/create/', views.CreateWalletView.as_view(), name='wallet_create'),
    path('wallets/<uuid:wallet_uuid>/', views.RetrieveWalletView.as_view(), name='wallet_detail'),
    path('wallets/<uuid:wallet_uuid>/update/', views.UpdateWalletView.as_view(), name='wallet_update'),
    path('wallets/<uuid:wallet_uuid>/delete/', views.DestroyWalletView.as_view(), name='wallet_delete'),
    path('wallets/<uuid:wallet_uuid>/operation/', views.WalletChangeBalanceView.as_view(), name='wallet_operation'),
]
