# Generated by Django 3.1.5 on 2021-06-09 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0041_sheetmusic_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
    ]
