# Generated by Django 3.1.5 on 2021-01-27 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0002_auto_20210122_0837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='composerprofile',
            name='phone_number',
        ),
    ]
