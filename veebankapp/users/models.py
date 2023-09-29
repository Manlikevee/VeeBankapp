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
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Add other fields as needed, and set them as blank=True and null=True
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = s
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username
