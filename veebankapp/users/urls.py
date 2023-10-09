from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_view
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import *
from .serializer import *

router = DefaultRouter()

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('sample/', SampleAPI.as_view(), name='sample-api'),
    path('userprofile/', userprofile, name='sample-userprofile'),
    path('transactions/', transactions, name='sample-transactions'),
    path('bank/resolve/<str:id>', get_account_details, name='get_account_details'),
    path('Newtransaction', donetransactionss, name='donetransactions'),
    path('BankAccounts', BankAccounts, name='BankAccounts'),
    path('new_transaction', new_transaction, name='new_transaction'),
    path('singletrans/<str:id>', singletrans, name='singletrans'),
    path('singletransbackup/<str:id>', singletransbackup, name='singletransbackup'),
    path('airtime', import_data_plans, name='import_data_plans'),
    path('outward', donetransactionsoutward, name='donetransactionsoutward'),
    path('donetransactionbill', donetransactionbill, name='donetransactionbill'),
    path('allbills', allbills, name='allbills'),
    path('creditanddebit', creditanddebit, name='creditanddebit'),
    path('generate_single_atm_card/', generate_single_atm_card, name='generate_single_atm_card'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('veebankregister/', UserRegistrationView.as_view(), name='user-registration'),
    path('imgtext/', imgtext, name='user-imgtext'),
    path('setpinandprofile/', setpinandprofile, name='setpinandprofile'),
    path('AvailableImages/', AvailableImages, name='AvailableImages'),
    path('Savebeneficiary/', Savebeneficiary, name='Savebeneficary'),


]
