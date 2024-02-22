# Generated by Django 4.2.5 on 2023-10-04 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_betting'),
    ]

    operations = [
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to='networkimg')),
            ],
        ),
        migrations.CreateModel(
            name='Giftcard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to='networkimg')),
            ],
        ),
        migrations.CreateModel(
            name='Power',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to='networkimg')),
            ],
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to='networkimg')),
            ],
        ),
        migrations.CreateModel(
            name='Tv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to='networkimg')),
            ],
        ),
    ]
