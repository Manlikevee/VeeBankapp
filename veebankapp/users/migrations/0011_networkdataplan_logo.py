# Generated by Django 4.2.5 on 2023-10-03 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_networkdataplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkdataplan',
            name='logo',
            field=models.ImageField(blank=True, upload_to='networkimg'),
        ),
    ]
