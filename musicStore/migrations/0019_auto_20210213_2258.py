# Generated by Django 3.1.5 on 2021-02-13 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0018_auto_20210213_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='background_image',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
