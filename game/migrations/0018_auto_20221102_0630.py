# Generated by Django 3.1.5 on 2022-11-02 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0017_auto_20221101_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
