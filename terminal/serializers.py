from rest_framework import serializers

from terminal.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('id', 'owner')

class OperationSerializer(serializers.Serializer):
    operation_type = serializers.ChoiceField(choices=['DEPOSIT', 'WITHDRAW'])
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate(self, attrs):
        amount = attrs.get('amount')
        operation_type = attrs.get('operation_type')
        wallet = self.context.get('wallet')

        if operation_type == 'WITHDRAW' and wallet.amount < amount:
            raise serializers.ValidationError('You do not have enough money.')
        return attrs
