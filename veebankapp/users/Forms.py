from rest_framework import serializers

class TransactionFormSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=4)
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    narration = serializers.CharField(max_length=100)