# Generated by Django 4.2.14 on 2024-08-02 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_phone_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
    ]
