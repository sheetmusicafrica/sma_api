# Generated by Django 3.1.5 on 2022-07-01 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0041_auto_20220701_1222'),
        ('payout', '0008_auto_20210509_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchpayout',
            name='composers_paid_to',
            field=models.ManyToManyField(blank=True, to='composer.ComposerProfile'),
        ),
    ]
