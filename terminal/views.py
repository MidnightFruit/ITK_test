from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, \
    get_object_or_404
from rest_framework.response import Response

from terminal.models import Wallet
from terminal.serializers import WalletSerializer, OperationSerializer


class CreateWalletView(CreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class RetrieveWalletView(RetrieveAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'wallet_uuid'
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class UpdateWalletView(UpdateAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'wallet_uuid'
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class DestroyWalletView(DestroyAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'wallet_uuid'
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class ListWalletView(ListAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class WalletChangeBalanceView(UpdateAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'wallet_uuid'

    def post(self, request, *args, **kwargs):
        wallet_uuid = kwargs['wallet_uuid']

        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(id=wallet_uuid)

                serializer = OperationSerializer(data=request.data, context={'wallet': wallet})

                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                operation_type = serializer.validated_data['operation_type']
                amount = serializer.validated_data['amount']

                if operation_type == 'WITHDRAW':
                    wallet.amount -= amount
                elif operation_type == 'DEPOSIT':
                    wallet.amount += amount

                wallet.save()

            return Response({
                'wallet_id': wallet.id,
                'amount': wallet.amount
            }, status=status.HTTP_200_OK)

        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
