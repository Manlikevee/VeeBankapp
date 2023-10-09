import requests
import shortuuid
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from faker import Faker
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.Forms import TransactionFormSerializer
from users.models import Profile, Transaction, BankAccount, TransactionType, donetransaction, NetworkDataPlan, Betting, \
    Transport, Tv, Power, ATMCard, Giftcard, Education, AvailableImage
from users.serializer import Completeprofile, Transactionsserializer, BankAccountserializer, Donetransaction, \
    TransactionTypeserializer, PostTransactionsserializer, NetworkDataPlanSerializer, BettingnSerializer, \
    TransportSerializer, TvSerializer, PowerSerializer, ATMCardSerializer, GiftcardPlanSerializer, EducationSerializer, \
    Userserializer, UserRegistrationSerializer, AvailableImageSerializer


# Create your views here.


class SampleAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated successfully."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userprofile(request):
    user = request.user
    Profile.objects.update_or_create(
        user=request.user)
    user_profile = Profile.objects.filter(user=user).first()
    userprofile = Completeprofile(user_profile)
    useraccount = BankAccount.objects.filter(user=user).first()
    useraccountdata = BankAccountserializer(useraccount)
    latesttransaction = donetransaction.objects.filter(user=user).last()

    if latesttransaction is not None:
        transactiondata = Donetransaction(latesttransaction)
    else:
        transactiondata = None

    context = {
        'userprofile': userprofile.data,
        'useraccountdata': useraccountdata.data,
        'transactiondata': transactiondata.data if transactiondata else None
    }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def BankAccounts(request):
    user = request.user
    useraccount = BankAccount.objects.filter(user=user).first()
    useraccountdata = BankAccountserializer(useraccount)

    context = {
        'useraccountdata': useraccountdata.data
    }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request):
    alltransactions = donetransaction.objects.filter(user=request.user).all().order_by('-id')
    transactiondata = Donetransaction(alltransactions, many=True)

    response_data = {
        'transactiondata': transactiondata.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def singletransbackup(request, id):
    try:
        alltransactions = donetransaction.objects.filter(user=request.user).filter(id=id).first()
        transactiondata = Donetransaction(alltransactions)

        return Response({'data': transactiondata.data}, status=status.HTTP_200_OK)
    except donetransaction.DoesNotExist:
        return Response({'data': 'Incorrect Details'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def singletrans(request, id):
    try:
        # Use get instead of filter to retrieve a single object or raise a DoesNotExist exception
        transaction = donetransaction.objects.get(id=id, user=request.user)
        # Serialize the transaction data using a serializer
        serializer = Donetransaction(transaction)  # Replace YourTransactionSerializer with your actual serializer

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except donetransaction.DoesNotExist:
        return Response({'data': 'Incorrect Details'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_account_details(request, id):
    try:
        bank_account = BankAccount.objects.get(account_number=id)
        serializer = BankAccountserializer(bank_account)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except BankAccount.DoesNotExist:
        return Response({'data': 'Incorrect Details'}, status=status.HTTP_400_BAD_REQUEST)


from decimal import Decimal


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def donetransactionss(request):
    my_user = request.user
    my_account = BankAccount.objects.filter(user=my_user).first()

    transaction_type = get_object_or_404(TransactionType, name='Fund Transfer')
    s = shortuuid.ShortUUID().random(length=20)
    if request.method == 'POST':
        pin = request.data.get('pin')
        account_number = request.data.get('account_number')
        amount = request.data.get('amount')
        narration = request.data.get('narration')
        pinprofile = Profile.objects.filter(user=my_user).filter(pin=pin).first()
        if my_account:
            if pinprofile:
                debit_amount = Decimal(amount)

                if my_account.balance >= debit_amount:
                    debit_bank = BankAccount.objects.filter(account_number=account_number).first()
                    if debit_bank:

                        serializer = PostTransactionsserializer(data={
                            'sender_bank_account': my_account.id,
                            'recipient_bank_account': debit_bank.id,
                            'sender_user': my_account.account_name,
                            'recipient_user': debit_bank.account_name,
                            'transaction_type': transaction_type.id,
                            'reference': s,
                            'amount': debit_amount,
                            'status': 'Completed',
                            'narration': narration,
                            'Bank_name': 'Vee Bank',
                            'Bank_accountnumber': account_number,
                            'is_debit': True,
                            'is_credit': False
                        })

                        if serializer.is_valid():
                            recipient_user = User.objects.get(username=debit_bank.user.username)
                            transaction_instance = serializer.save()

                            sender_record = donetransaction.objects.create(
                                user=my_user,
                                status='Completed',
                                transaction=transaction_instance,
                                amount=debit_amount,
                                is_debit=True,
                                is_fundtransfer=True
                            )

                            recipient_record = donetransaction.objects.create(
                                user=recipient_user,
                                status='Completed',
                                transaction=transaction_instance,
                                amount=debit_amount,
                                is_credit=True,
                                is_fundtransfer=True
                            )
                            my_account.balance = my_account.balance - debit_amount
                            my_account.save()

                            debit_bank.balance = debit_bank.balance + debit_amount
                            debit_bank.save()
                            transaction_serializer = Transactionsserializer(transaction_instance)
                            return Response(transaction_serializer.data, status=status.HTTP_200_OK)


                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Insufficient Funds'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Wrong Pin'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


def verify_account(account_number, bank_code):
    paystack_secret_key = 'sk_test_c1f886a70706e4f3e7ae82860d178f6d48a4822c'

    # Create the Paystack verify account endpoint URL
    verify_url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"

    # Make a GET request to the Paystack API
    headers = {
        'Authorization': f'Bearer {paystack_secret_key}',
        'Content-Type': 'application/json',
    }

    response = requests.get(verify_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(data)
        account_name = data.get('data', {}).get('account_name', '')
        return {'status': 'success', 'account_name': account_name}
    else:
        return {'status': 'error', 'message': 'Unable to verify account number'}


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def donetransactionsoutward(request):
    my_user = request.user
    my_account = BankAccount.objects.filter(user=my_user).first()
    transaction_type = get_object_or_404(TransactionType, name='Fund Transfer')
    s = shortuuid.ShortUUID().random(length=20)
    if request.method == 'POST':
        pin = request.data.get('pin')
        account_number = request.data.get('account_number')
        bank_code = request.data.get('bankcode')
        bank_name = request.data.get('bankname')
        amount = request.data.get('amount')
        narration = request.data.get('narration')
        pinprofile = Profile.objects.filter(user=my_user).filter(pin=pin).first()
        if my_account:
            if pinprofile:
                debit_amount = Decimal(amount)
                if my_account.balance >= debit_amount:
                    debit_bank = verify_account(account_number, bank_code)
                    if debit_bank:
                        serializer = PostTransactionsserializer(data={
                            'sender_bank_account': my_account.id,
                            'sender_user': my_account.account_name,
                            'recipient_user': debit_bank.get('account_name', ''),
                            'transaction_type': transaction_type.id,
                            'reference': s,
                            'amount': debit_amount,
                            'status': 'Completed',
                            'narration': narration,
                            'Bank_name': bank_name,
                            'Bank_accountnumber': account_number,
                            'is_debit': True,
                            'is_credit': False
                        })
                        if serializer.is_valid():
                            transaction_instance = serializer.save()
                            print(transaction_instance)
                            sender_record = donetransaction.objects.create(
                                user=my_user,
                                status='Completed',
                                transaction=transaction_instance,
                                amount=debit_amount,
                                is_debit=True,
                                is_fundtransfer=True
                            )

                            my_account.balance = my_account.balance - debit_amount
                            my_account.save()

                            transaction_serializer = Transactionsserializer(transaction_instance)
                            return Response(transaction_serializer.data, status=status.HTTP_200_OK)


                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Insufficient Funds'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Wrong Pin'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def donetransactionbill(request):
    my_user = request.user
    my_account = BankAccount.objects.filter(user=my_user).first()
    transaction_type = get_object_or_404(TransactionType, name='Bill Payment')
    s = shortuuid.ShortUUID().random(length=20)
    if request.method == 'POST':
        pin = request.data.get('pin')
        phonenumber = request.data.get('phonenumber')
        Network = request.data.get('network')
        amount = request.data.get('amount')
        narration = request.data.get('narration')
        pinprofile = Profile.objects.filter(user=my_user).filter(pin=pin).first()
        if my_account:
            if pinprofile:
                debit_amount = Decimal(amount)
                if my_account.balance >= debit_amount:
                    debit_bank = 'Billpayment'
                    if debit_bank:
                        serializer = PostTransactionsserializer(data={
                            'sender_bank_account': my_account.id,
                            'sender_user': my_account.account_name,
                            'recipient_user': Network,
                            'transaction_type': transaction_type.id,
                            'reference': s,
                            'amount': debit_amount,
                            'status': 'Completed',
                            'narration': narration,
                            'Bank_name': Network,
                            'Bank_accountnumber': phonenumber,
                            'is_debit': True,
                            'is_credit': False
                        })
                        if serializer.is_valid():
                            transaction_instance = serializer.save()
                            print(transaction_instance)
                            sender_record = donetransaction.objects.create(
                                user=my_user,
                                status='Completed',
                                transaction=transaction_instance,
                                amount=debit_amount,
                                is_debit=True,
                                is_billpayment=True
                            )

                            my_account.balance = my_account.balance - debit_amount
                            my_account.save()

                            transaction_serializer = Transactionsserializer(transaction_instance)
                            return Response(transaction_serializer.data, status=status.HTTP_200_OK)


                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Insufficient Funds'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Wrong Pin'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def donetransactionbill(request):
    my_user = request.user
    my_account = BankAccount.objects.filter(user=my_user).first()
    transaction_type = get_object_or_404(TransactionType, name='Bill Payment')
    s = shortuuid.ShortUUID().random(length=20)
    if request.method == 'POST':
        pin = request.data.get('pin')
        phonenumber = request.data.get('phonenumber')
        Network = request.data.get('network')
        amount = request.data.get('amount')
        narration = request.data.get('narration')
        pinprofile = Profile.objects.filter(user=my_user).filter(pin=pin).first()
        if my_account:
            if pinprofile:
                debit_amount = Decimal(amount)
                if my_account.balance >= debit_amount:
                    debit_bank = 'Billpayment'
                    if debit_bank:
                        serializer = PostTransactionsserializer(data={
                            'sender_bank_account': my_account.id,
                            'sender_user': my_account.account_name,
                            'recipient_user': Network,
                            'transaction_type': transaction_type.id,
                            'reference': s,
                            'amount': debit_amount,
                            'status': 'Completed',
                            'narration': narration,
                            'Bank_name': Network,
                            'Bank_accountnumber': phonenumber,
                            'is_debit': True,
                            'is_credit': False
                        })
                        if serializer.is_valid():
                            transaction_instance = serializer.save()
                            print(transaction_instance)
                            sender_record = donetransaction.objects.create(
                                user=my_user,
                                status='Completed',
                                transaction=transaction_instance,
                                amount=debit_amount,
                                is_debit=True,
                                is_billpayment=True
                            )

                            my_account.balance = my_account.balance - debit_amount
                            my_account.save()

                            transaction_serializer = Transactionsserializer(transaction_instance)
                            return Response(transaction_serializer.data, status=status.HTTP_200_OK)


                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Insufficient Funds'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Wrong Pin'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Account Not Found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


import json


@api_view(['POST'])
def new_transaction(request):
    if request.method == 'POST':
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        pin = data.get('pin')
        account_number = data.get('account_number')
        amount = data.get('amount')
        narration = data.get('narration')

        # Now you can use pin, account_number, amount, and narration as expected
        # ... Your transaction handling logic ...

        return Response({'detail': 'Success'}, status=status.HTTP_200_OK)

    return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST', 'GET'])
def import_data_plans(request):
    # dataPlans = [
    #     {
    #         "network": "Airtel",
    #         "plans": [
    #             {"name": "Airtel Daily 50MB", "price": 100, "data": "50MB", "validity": "1 day"},
    #             {"name": "Airtel Weekly 200MB", "price": 350, "data": "200MB", "validity": "7 days"},
    #             {"name": "Airtel Monthly 1GB", "price": 1000, "data": "1GB", "validity": "30 days"},
    #             {"name": "Airtel Monthly 2GB", "price": 2000, "data": "2GB", "validity": "30 days"},
    #             {"name": "Airtel Monthly 5GB", "price": 3500, "data": "5GB", "validity": "30 days"},
    #             {"name": "Airtel Night 500MB", "price": 200, "data": "500MB", "validity": "Night"},
    #             {"name": "Airtel Night 1GB", "price": 350, "data": "1GB", "validity": "Night"},
    #             {"name": "Airtel Mega 10GB", "price": 5000, "data": "10GB", "validity": "30 days"},
    #             {"name": "Airtel Mega 20GB", "price": 8000, "data": "20GB", "validity": "30 days"},
    #             {"name": "Airtel Mega 50GB", "price": 15000, "data": "50GB", "validity": "30 days"},
    #         ],
    #     },
    #     {
    #         "network": "MTN",
    #         "plans": [
    #             {"name": "MTN Daily 50MB", "price": 100, "data": "50MB", "validity": "1 day"},
    #             {"name": "MTN Weekly 350MB", "price": 350, "data": "350MB", "validity": "7 days"},
    #             {"name": "MTN Monthly 1.5GB", "price": 1000, "data": "1.5GB", "validity": "30 days"},
    #             {"name": "MTN Monthly 3GB", "price": 2000, "data": "3GB", "validity": "30 days"},
    #             {"name": "MTN Monthly 10GB", "price": 5000, "data": "10GB", "validity": "30 days"},
    #             {"name": "MTN Night 500MB", "price": 200, "data": "500MB", "validity": "Night"},
    #             {"name": "MTN Night 1GB", "price": 350, "data": "1GB", "validity": "Night"},
    #             {"name": "MTN Mega 20GB", "price": 8000, "data": "20GB", "validity": "30 days"},
    #             {"name": "MTN Mega 40GB", "price": 12000, "data": "40GB", "validity": "30 days"},
    #             {"name": "MTN Mega 100GB", "price": 25000, "data": "100GB", "validity": "30 days"},
    #         ],
    #     },
    #     {
    #         "network": "Glo",
    #         "plans": [
    #             {"name": "Glo Daily 50MB", "price": 100, "data": "50MB", "validity": "1 day"},
    #             {"name": "Glo Weekly 500MB", "price": 350, "data": "500MB", "validity": "7 days"},
    #             {"name": "Glo Monthly 2GB", "price": 1000, "data": "2GB", "validity": "30 days"},
    #             {"name": "Glo Monthly 4.5GB", "price": 2000, "data": "4.5GB", "validity": "30 days"},
    #             {"name": "Glo Monthly 12GB", "price": 5000, "data": "12GB", "validity": "30 days"},
    #             {"name": "Glo Night 1GB", "price": 200, "data": "1GB", "validity": "Night"},
    #             {"name": "Glo Night 2GB", "price": 350, "data": "2GB", "validity": "Night"},
    #             {"name": "Glo Mega 30GB", "price": 8000, "data": "30GB", "validity": "30 days"},
    #             {"name": "Glo Mega 60GB", "price": 15000, "data": "60GB", "validity": "30 days"},
    #             {"name": "Glo Mega 120GB", "price": 25000, "data": "120GB", "validity": "30 days"},
    #         ],
    #     },
    #     {
    #         "network": "9Mobile",
    #         "plans": [
    #             {"name": "9Mobile Daily 40MB", "price": 100, "data": "40MB", "validity": "1 day"},
    #             {"name": "9Mobile Weekly 150MB", "price": 350, "data": "150MB", "validity": "7 days"},
    #             {"name": "9Mobile Monthly 1GB", "price": 1000, "data": "1GB", "validity": "30 days"},
    #             {"name": "9Mobile Monthly 2.5GB", "price": 2000, "data": "2.5GB", "validity": "30 days"},
    #             {"name": "9Mobile Monthly 5GB", "price": 3500, "data": "5GB", "validity": "30 days"},
    #             {"name": "9Mobile Night 500MB", "price": 200, "data": "500MB", "validity": "Night"},
    #             {"name": "9Mobile Night 1GB", "price": 350, "data": "1GB", "validity": "Night"},
    #             {"name": "9Mobile Mega 40GB", "price": 8000, "data": "40GB", "validity": "30 days"},
    #             {"name": "9Mobile Mega 80GB", "price": 15000, "data": "80GB", "validity": "30 days"},
    #             {"name": "9Mobile Mega 150GB", "price": 25000, "data": "150GB", "validity": "30 days"},
    #         ],
    #     },
    #     {
    #         "network": "Ntel",
    #         "plans": [
    #             {"name": "Ntel Daily 50MB", "price": 100, "data": "50MB", "validity": "1 day"},
    #             {"name": "Ntel Weekly 500MB", "price": 350, "data": "500MB", "validity": "7 days"},
    #             {"name": "Ntel Monthly 2GB", "price": 1000, "data": "2GB", "validity": "30 days"},
    #             {"name": "Ntel Monthly 4.5GB", "price": 2000, "data": "4.5GB", "validity": "30 days"},
    #             {"name": "Ntel Monthly 10GB", "price": 5000, "data": "10GB", "validity": "30 days"},
    #             {"name": "Ntel Night 1GB", "price": 200, "data": "1GB", "validity": "Night"},
    #             {"name": "Ntel Night 2GB", "price": 350, "data": "2GB", "validity": "Night"},
    #             {"name": "Ntel Mega 30GB", "price": 8000, "data": "30GB", "validity": "30 days"},
    #             {"name": "Ntel Mega 60GB", "price": 15000, "data": "60GB", "validity": "30 days"},
    #             {"name": "Ntel Mega 120GB", "price": 25000, "data": "120GB", "validity": "30 days"},
    #         ],
    #     },
    # ]
    #
    # for plan_data in dataPlans:
    #     plans_json = plan_data['plans']
    #     NetworkDataPlan.objects.create(network=plan_data['network'], plans=plans_json)

    queryset = NetworkDataPlan.objects.all()
    serializer_class = NetworkDataPlanSerializer(queryset, many=True)
    return Response(serializer_class.data, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
def allbills(request):
    queryset = NetworkDataPlan.objects.all()
    serializer_class = NetworkDataPlanSerializer(queryset, many=True)
    qs2 = Betting.objects.all()
    bettngdata = BettingnSerializer(qs2, many=True)
    trans = Transport.objects.all()
    transdata = TransportSerializer(trans, many=True)
    tvseries = Tv.objects.all()
    tvdata = TvSerializer(tvseries, many=True)
    powers = Power.objects.all()
    powerdata = PowerSerializer(powers, many=True)
    giftcard = Giftcard.objects.all()
    gift = GiftcardPlanSerializer(giftcard, many=True)
    edu = Education.objects.all()
    education = EducationSerializer(edu, many=True)
    response_data = {

        'betting': bettngdata.data,
        'transport': transdata.data,
        'tv': tvdata.data,
        'power': powerdata.data,
        'airtime': serializer_class.data,
        'giftcards': gift.data,
        'educations': education.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def creditanddebit(request):
    user = request.user
    usercredits = donetransaction.objects.filter(is_credit=True).filter(user=user).all()
    userstransactions = donetransaction.objects.filter(user=user).all()

    usercredit = Donetransaction(usercredits, many=True)
    userdebits = donetransaction.objects.filter(is_debit=True).filter(user=user).all()
    userdebit = Donetransaction(userdebits, many=True)
    usercreditbalance = donetransaction.objects.filter(is_credit=True).filter(user=user).all().aggregate(
        Sum('amount'))
    userdebitbalance = donetransaction.objects.filter(is_debit=True).filter(user=user).all().aggregate(
        Sum('amount'))
    userstransaction = Donetransaction(userstransactions, many=True)
    context = {
        'usercreditbalance': usercreditbalance,
        'userdebitbalance': userdebitbalance,
        'usercreditdata': usercredit.data,
        'userdebit': userdebit.data,
        'userstransaction': userstransaction.data

    }
    return Response(context, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def generate_single_atm_card(request):
    user = User.objects.filter(id=1).first()
    card = ATMCard.objects.filter(user=user).first()

    if card:
        # If the user already has a card, return its details
        serializer = ATMCardSerializer(card)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        # If the user doesn't have a card, generate one using Faker
        fake = Faker()
        card_type = fake.credit_card_provider()
        card_number = fake.credit_card_number(card_type=None)
        expiry_date = fake.credit_card_expire(start="now", end="+10y", date_format="%m/%y")
        ccv = fake.credit_card_security_code(card_type=None)

        # Create a new ATM card for the user
        card = ATMCard.objects.create(
            user=user,  # Assuming 'user' is the ForeignKey field
            card_type=card_type,
            card_number=card_number,
            expiry_date=expiry_date,
            ccv=ccv,
        )

        serializer = ATMCardSerializer(card)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegistrationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        firstname = request.data.get('first_name')
        lastname = request.data.get('last_name')
        password = request.data.get('password')

        if not (username and email and firstname and lastname and password):
            return Response({'error': 'Please fill in all fields.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname
        )

        return Response({'success': 'User registered successfully.'}, status=status.HTTP_201_CREATED)


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            firstname = serializer.validated_data['first_name']
            lastname = serializer.validated_data['last_name']
            password = serializer.validated_data['password']

            # Check if the username or email already exists
            if User.objects.filter(username=username).filter(email=email).exists():
                return Response({'error': 'User with Username and Email already exists'},
                                status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the user
            user = serializer.save()

            return Response({'message': 'User registered successfully'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def imgtext(request):
    likke = Profile.objects.filter(id=7).first()
    likke.profilephoto = 'https://res.cloudinary.com/viktortech/image/upload/v1/media/networkimg/image_original4_uypyxl'
    likke.save()


@api_view(['GET'])
def AvailableImages(request):
    s = shortuuid.ShortUUID(alphabet="0123456789")
    accno = s.random(length=10)

    my_user = request.user
    my_accountname = f"{my_user.first_name} {my_user.last_name}"
    my_account, created = BankAccount.objects.get_or_create(
        user=my_user,
        defaults={"account_number": accno, "account_name": my_accountname}
    )
    avail = AvailableImage.objects.all()
    availdata = AvailableImageSerializer(avail, many=True)

    context = {
        'availdatas': availdata.data,

    }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
def setpinandprofile(request):
    transaction_type = get_object_or_404(TransactionType, name='Fund Transfer')
    if request.method == 'GET':
        return Response({'detail': 'GET request not supported'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    s = shortuuid.ShortUUID(alphabet="0123456789")
    accno = s.random(length=10)
    sap = s.random(length=16)

    my_user = request.user

    # Ensure the user exists before proceeding
    if not my_user:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    my_accountname = f"{my_user.first_name} {my_user.last_name}"
    myprofile, created = Profile.objects.get_or_create(user=my_user)

    my_account, created = BankAccount.objects.get_or_create(
        user=my_user,
        defaults={"account_number": accno, "account_name": my_accountname}
    )

    if request.method == 'POST':
        pin = request.data.get('pin')
        selectedimg = request.data.get('imgid')

        selectedimage = AvailableImage.objects.filter(id=selectedimg).first()

        if not myprofile.is_verified:
            myprofile.profile_image = selectedimage
            myprofile.pin = pin
            myprofile.is_verified = True  # Assuming you want to mark the profile as verified
            myprofile.save()
            serializer = PostTransactionsserializer(data={
                'sender_user': 'VeeBank',
                'recipient_bank_account': my_account.id,
                'recipient_user': my_account.account_name,
                'transaction_type': transaction_type.id,
                'reference': sap,
                'amount': 300000,
                'status': 'Completed',
                'narration': 'SIGN ON BONUS',
                'Bank_name': 'Vee Bank',
                'Bank_accountnumber': my_account.account_number,
                'is_debit': False,
                'is_credit': True
            })

            if serializer.is_valid():
                recipient_user = request.user
                transaction_instance = serializer.save()

                sender_record = donetransaction.objects.create(
                    user=my_user,
                    status='Completed',
                    transaction=transaction_instance,
                    amount=300000,
                    is_credit=True,
                    is_fundtransfer=True
                )
                my_account.balance = my_account.balance + 300000
                my_account.save()

                transaction_serializer = Transactionsserializer(transaction_instance)
                return Response(transaction_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Profile Already Set'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Profile and PIN updated successfully'}, status=status.HTTP_200_OK)
