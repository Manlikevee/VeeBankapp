from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import Profile, Transaction, BankAccount
from users.serializer import Completeprofile, Transactionsserializer, BankAccountserializer


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
def transactions(request):
    alltransactions = Transaction.objects.all()
    transactiondata = Transactionsserializer(alltransactions, many=True)

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