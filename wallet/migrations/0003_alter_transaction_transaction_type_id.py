# Generated by Django 3.2.9 on 2022-02-17 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_alter_wallet_wallet_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type_id',
            field=models.CharField(max_length=40),
        ),
    ]