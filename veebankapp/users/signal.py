import shortuuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from faker import Faker

from users.models import Profile, ATMCard, BankAccount

s = shortuuid.ShortUUID(alphabet="0123456789")
otp = s.random(length=15)
accno = s.random(length=10)
fake = Faker()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.update_or_create(user=instance,
                                         defaults={'user': instance, "auth_token": otp})

        BankAccount.objects.update_or_create(user=instance,
                                             defaults={'user': instance, "account_number": accno})

        card_type = fake.credit_card_provider()
        card_number = fake.credit_card_number(card_type=None)
        expiry_date = fake.credit_card_expire(start="now", end="+10y", date_format="%m/%y")
        ccv = fake.credit_card_security_code(card_type=None)
        ATMCard.objects.update_or_create(
            user=instance,  # Assuming 'user' is the ForeignKey field
            defaults={
                'card_type': card_type,
                'card_number': card_number,
                'expiry_date': expiry_date,
                'ccv': ccv,
            }
        )
