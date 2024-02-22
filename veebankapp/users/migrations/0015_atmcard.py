# Generated by Django 4.2.5 on 2023-10-06 16:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0014_utilty'),
    ]

    operations = [
        migrations.CreateModel(
            name='ATMCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_type', models.CharField(blank=True, max_length=255, null=True)),
                ('card_number', models.CharField(blank=True, max_length=16, null=True)),
                ('expiry_date', models.CharField(blank=True, max_length=5, null=True)),
                ('ccv', models.CharField(blank=True, max_length=4, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]