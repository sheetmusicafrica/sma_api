# Generated by Django 3.1.5 on 2021-05-14 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0038_score_sale_seller_revenue'),
    ]

    operations = [
        migrations.AddField(
            model_name='sheetmusic',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
    ]
