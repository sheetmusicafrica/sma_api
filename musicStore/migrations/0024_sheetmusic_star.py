# Generated by Django 3.1.5 on 2021-03-08 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0023_auto_20210304_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='sheetmusic',
            name='star',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
