# Generated by Django 3.1.5 on 2021-02-12 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0013_auto_20210212_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='score_sale',
            name='purchased',
            field=models.BooleanField(default=False),
        ),
    ]