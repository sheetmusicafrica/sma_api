# Generated by Django 3.1.5 on 2021-02-12 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0009_auto_20210212_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sheetmusic',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
