# Generated by Django 3.1.5 on 2021-03-04 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0021_sheetmusic_discription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sheetmusic',
            name='currency',
        ),
    ]