# Generated by Django 4.2.5 on 2023-10-01 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_bankaccount_account_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccount',
            name='bank',
            field=models.CharField(blank=True, default='Vee Bank', max_length=90, null=True),
        ),
    ]
