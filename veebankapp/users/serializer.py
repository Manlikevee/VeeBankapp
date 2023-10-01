from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Customize the token data here
        token['username'] = user.username
        token['email'] = user.email

        return token



class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'id']  # Or specify the fields you want to expose



class Completeprofile(serializers.ModelSerializer):
    user = Userserializer()

    class Meta:
        model = Profile
        fields = '__all__'  # Or specify the fields you want to expose

class BankAccountserializer(serializers.ModelSerializer):
    user = Userserializer()
    class Meta:
        model = BankAccount
        fields = '__all__'  # Or specify the fields you want to expose


class TransactionTypeserializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = '__all__'  # Or specify the fields you want to expose



class Transactionsserializer(serializers.ModelSerializer):
    sender_bank_account = BankAccountserializer()
    recipient_bank_account = BankAccountserializer()
    transaction_type = TransactionTypeserializer()

    class Meta:
        model = Transaction
        fields = '__all__'  # Or specify the fields you want to expose