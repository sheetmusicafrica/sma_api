# Generated by Django 3.1.5 on 2021-06-09 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0038_auto_20210609_0950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpaymenthistory',
            name='cart_id',
        ),
    ]
