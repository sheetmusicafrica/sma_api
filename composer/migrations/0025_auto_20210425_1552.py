# Generated by Django 3.1.5 on 2021-04-25 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0024_auto_20210425_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='composerprofile',
            name='state',
        ),
        migrations.AlterField(
            model_name='composerprofile',
            name='country',
            field=models.CharField(blank=True, default='Nigeria', max_length=100),
        ),
    ]
