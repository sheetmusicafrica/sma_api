# Generated by Django 3.1.5 on 2021-05-14 10:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0032_auto_20210509_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpaymentlog',
            name='date',
            field=models.DateField(default=datetime.date(2021, 5, 14)),
        ),
    ]