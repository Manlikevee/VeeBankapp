import shortuuid
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.Forms import TransactionFormSerializer
from users.models import Profile, Transaction, BankAccount, TransactionType, donetransaction
from users.serializer import Completeprofile, Transactionsserializer, BankAccountserializer, Donetransaction, \
    TransactionTypeserializer, PostTransactionsserializer


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

    context = {
        'userprofile': userprofile.data
    }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request):
    alltransactions = donetransaction.objects.all()
    transactiondata = Donetransaction(alltransactions, many=True)

    response_data = {
        'transactiondata': transactiondata.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


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
def donetransactionss(request):
    my_user = User.objects.filter(id=1).first()
    my_account = BankAccount.objects.filter(user=my_user).first()

    transaction_type = get_object_or_404(TransactionType, name='Fund Transfer')
    s = shortuuid.ShortUUID().random(length=20)
    if request.method == 'GET':
        form_serializer = TransactionFormSerializer()
        return Response({'form': form_serializer.data})
    if request.method == 'POST':
        pin = request.data.get('pin')
        account_number = request.data.get('account_number')
        amount = request.data.get('amount')
        narration = request.data.get('narration')
        user_profile = get_object_or_404(Profile, user=my_user)
        if my_account:
            if pin == user_profile.pin:
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

                            return Response(serializer.data, status=status.HTTP_200_OK)


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

    return JsonResponse({'saved': False, 'message': 'Invalid request method'})




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
