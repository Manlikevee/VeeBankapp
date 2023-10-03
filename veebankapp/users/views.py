import requests
import shortuuid
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.Forms import TransactionFormSerializer
from users.models import Profile, Transaction, BankAccount, TransactionType, donetransaction, NetworkDataPlan
from users.serializer import Completeprofile, Transactionsserializer, BankAccountserializer, Donetransaction, \
    TransactionTypeserializer, PostTransactionsserializer, NetworkDataPlanSerializer


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
    context = {
        'userprofile': userprofile.data,
        'useraccountdata': useraccountdata.data
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
                            print(transaction_instance)
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
        bank_code =  request.data.get('bankcode')
        bank_name =  request.data.get('bankname')
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
