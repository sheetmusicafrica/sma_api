# Generated by Django 3.1.5 on 2021-05-09 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0031_auto_20210509_0728'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpaymenthistory',
            name='payout_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userpaymenthistory',
            name='payment_type',
            field=models.CharField(default='payin', max_length=100),
        ),
    ]
