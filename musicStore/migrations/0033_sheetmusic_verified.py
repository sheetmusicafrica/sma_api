# Generated by Django 3.1.5 on 2021-04-26 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0032_score_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='sheetmusic',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
