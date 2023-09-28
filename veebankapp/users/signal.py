import shortuuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile

s = shortuuid.ShortUUID(alphabet="0123456789")
otp = s.random(length=15)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.update_or_create(user=instance,
                                         defaults={'user': instance, "auth_token": otp})
