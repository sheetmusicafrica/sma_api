# Generated by Django 3.1.5 on 2021-04-30 10:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0027_auto_20210428_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpaymentlog',
            name='date',
            field=models.DateField(default=datetime.date(2021, 4, 30)),
        ),
    ]
