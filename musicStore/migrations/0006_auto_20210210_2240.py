# Generated by Django 3.1.5 on 2021-02-10 21:40

from django.db import migrations, models
import sheet_music_africa.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0005_sheetmusic_myfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sheet_order',
            name='quantity',
        ),
        migrations.AlterField(
            model_name='sheetmusic',
            name='myfile',
            field=models.FileField(blank=True, null=True, storage=sheet_music_africa.storage_backends.PrivateMediaStorage(), upload_to=''),
        ),
    ]
