# Generated by Django 4.2.5 on 2023-10-05 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_education_giftcard_power_transport_tv'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utilty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to='networkimg')),
            ],
        ),
    ]
