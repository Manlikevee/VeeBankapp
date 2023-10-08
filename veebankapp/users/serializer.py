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


class PostTransactionsserializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['sender_bank_account', 'recipient_bank_account', 'sender_user', 'recipient_user', 'transaction_type',
                  'reference', 'amount', 'status', 'narration', 'Bank_name', 'Bank_accountnumber', 'is_debit',
                  'is_credit',  'created_at']


class Donetransaction(serializers.ModelSerializer):
    transaction = PostTransactionsserializer()

    class Meta:
        model = donetransaction
        fields = '__all__'  # Or specify the fields you want to expose


class NetworkDataPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDataPlan
        fields = '__all__'

class BettingnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Betting
        fields = '__all__'

class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = '__all__'

class TvSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tv
        fields = '__all__'


class PowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Power
        fields = '__all__'


class ATMCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATMCard
        fields = '__all__'


class NetworkDataPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDataPlan
        fields = '__all__'


class GiftcardPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Giftcard
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
