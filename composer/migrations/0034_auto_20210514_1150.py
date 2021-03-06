# Generated by Django 3.1.5 on 2021-05-14 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0033_auto_20210514_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpaymenthistory',
            name='bank_name_paid_to',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='userpaymenthistory',
            name='bank_paid_to',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='userpaymenthistory',
            name='email_paid_to',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
