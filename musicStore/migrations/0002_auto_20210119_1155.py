# Generated by Django 3.1.5 on 2021-01-19 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sheetmusic',
            name='sheet',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]