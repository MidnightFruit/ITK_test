import threading
import time
from decimal import Decimal
from functools import total_ordering
from http.client import responses

from django.core.serializers import serialize
from django.db import connections, transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from terminal.models import *
from terminal.serializers import OperationSerializer


class WalletAPITestCase(APITestCase):

    def setUp(self):
        self.wallet1 = Wallet.objects.create(balance=100)
        self.wallet2 = Wallet.objects.create(balance=0)
        self.wallet_uuid1 = self.wallet1.id
        self.wallet_uuid2 = self.wallet2.id

    def test_create_wallet(self):
        """
        Тестирование создания нового кошелька.
        """
        data = {
            "balance": 1000,
        }
        response = self.client.post('/api/v1/wallets/create/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_wallet(self):
        """
        Тестирование проверки баланса.
        """
        response = self.client.get(
            reverse('terminal:wallet_detail', args=[self.wallet_uuid1])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_wallet(self):
        """
        Тестирование просмотра всех кошельков.
        """
        response = self.client.get(reverse('terminal:wallet_list'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(len(response.data), 2)

        expected_data = [
                {'id': str(self.wallet1.id), 'balance': '100.00'},
                {'id': str(self.wallet2.id), 'balance': '0.00'}
            ]
        self.assertEqual(response.data, expected_data)

    def test_update_wallet(self):
        """
        Тестирование изменения кошелька.
        """

        response = self.client.patch(reverse("terminal:wallet_update", args=[self.wallet_uuid1]), {"balance": 0})

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        wallet = Wallet.objects.get(id=self.wallet_uuid1)
        self.assertEqual(wallet.balance, 0)

    def test_destroy_wallet(self):
        """
        Тестирование удаления кошелька.
        """

        responses = self.client.delete(reverse("terminal:wallet_delete", args=[self.wallet_uuid1]))

        self.assertEqual(
            responses.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_deposit_operation_wallet(self):
        """
        Тестирование операции пополнения.
        """
        init_balance = self.wallet1.balance
        deposit = 100
        expected_result = init_balance + deposit
        data = {
            "operation_type": "DEPOSIT",
            "amount": deposit
        }
        response = self.client.post(
            reverse('terminal:wallet_operation', kwargs={'wallet_uuid': self.wallet_uuid1}),
            data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, expected_result)
        self.assertEqual(response.data['balance'], Decimal(str(expected_result)))

    def test_withdraw_operation_wallet(self):
        """
        Тестирование операции снятия.
        """
        init_balance = self.wallet1.balance
        withdraw = 100
        expected_result = init_balance - withdraw
        data = {
            "operation_type": "WITHDRAW",
            "amount": withdraw
        }
        response = self.client.post(
            reverse('terminal:wallet_operation', kwargs={'wallet_uuid': self.wallet_uuid1}),
            data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, expected_result)
        self.assertEqual(response.data['balance'], Decimal(str(expected_result)))

    def test_withdraw_insufficient_funds(self):
        """
        Тестирование случая недостатка средств.
        """
        init_balance = self.wallet1.balance
        withdraw = init_balance + 1
        data = {
            "operation_type": "WITHDRAW",
            "amount": withdraw
        }

        self.assertGreater(withdraw, init_balance)

        response = self.client.post(
            reverse('terminal:wallet_operation', kwargs={'wallet_uuid': self.wallet_uuid1}),
            data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, init_balance)
        self.assertIn('non_field_errors', response.data)

    def test_wallet_not_found(self):
        """
        Тестирование случая запроса к несуществующему кошельку.
        """
        non_existent_uuid = '00000000-0000-0000-0000-000000000000'
        data = {
            "operation_type": "DEPOSIT",
            "amount": 100
        }

        response = self.client.post(
            reverse('terminal:wallet_operation', kwargs={'wallet_uuid': non_existent_uuid}),
            data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Wallet not found')
