from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from terminal.models import *


class WalletAPITestCase(APITestCase):

    def setUp(self):
        self.wallet = Wallet.objects.create(amount=100)
        self.wallet_uuid = self.wallet.id

    def test_create_wallet(self):
        """
        Тестирование создания нового кошелька
        """
        data = {
            "amount": 1000,
        }
        response = self.client.post('/api/v1/wallets/create/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)