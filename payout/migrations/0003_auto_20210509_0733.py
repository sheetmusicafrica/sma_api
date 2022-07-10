# Generated by Django 3.1.5 on 2021-05-09 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payout', '0002_batchpayout_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchpayout',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='batchpayout',
            name='batch_number',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
