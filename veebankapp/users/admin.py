from django.contrib import admin
from .models import Profile, Transaction, BankAccount, TransactionType, donetransaction, NetworkDataPlan
# Register your models here.
admin.site.register(Profile)
admin.site.register(Transaction)
admin.site.register(BankAccount)
admin.site.register(TransactionType)
admin.site.register(donetransaction)
admin.site.register(NetworkDataPlan)