from django.contrib.auth.models import User
from django.db import models
import shortuuid

s = shortuuid.ShortUUID().random(length=10)
# Create your models here.


class Profile(models.Model):
    Workstatus = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=100, blank=True, choices=Workstatus)
    form_of_id = models.CharField(blank=True, max_length=600)
    id_number = models.BigIntegerField(default=0000, blank=True)
    job_title = models.CharField(blank=True, max_length=600)
    country = models.CharField(blank=True, max_length=600)
    city = models.CharField(blank=True, max_length=600)
    region = models.CharField(blank=True, max_length=600)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    account_number = models.CharField(max_length=20, unique=True, blank=True, null=True, default=None)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    # Add other fields as needed, and set them as blank=True and null=True
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = s
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username


# Define a model for the user's bank account
class BankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.account_number

# Define a model for transaction types
class TransactionType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Define a model for transactions
class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    sender_bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sent_transactions', null=True, blank=True)
    recipient_bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    sender_user = models.CharField(max_length=100, null=True, blank=True)
    recipient_user = models.CharField(max_length=100, null=True, blank=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='Pending')
    payment_data = models.JSONField(null=True, blank=True)
    narration = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    Bank_name = models.CharField(max_length=100, default='')
    Bank_accountnumber = models.CharField(max_length=100 ,default='')
    transfer_payment = models.JSONField(null=True, blank=True)
    bill_payment = models.JSONField(null=True, blank=True)
    # Credit or Debit
    is_credit = models.BooleanField(default=False)
    is_debit = models.BooleanField(default=False)

    # Reversal
    is_reversal = models.BooleanField(default=False)
    original_transaction = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f" {self.reference} + {self.sender_user}"

# Define choices for transaction status




