# Generated by Django 3.1.5 on 2021-02-13 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0016_auto_20210213_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score_sale',
            name='date_purchased',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='score_sale',
            name='purchased_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
