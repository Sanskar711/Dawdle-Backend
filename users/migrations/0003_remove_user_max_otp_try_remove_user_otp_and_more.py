# Generated by Django 4.2.14 on 2024-07-31 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_max_otp_try_user_otp_user_otp_expiry_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='max_otp_try',
        ),
        migrations.RemoveField(
            model_name='user',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='user',
            name='otp_expiry',
        ),
        migrations.RemoveField(
            model_name='user',
            name='otp_max_out',
        ),
    ]
