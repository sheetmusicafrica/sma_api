# Generated by Django 3.1.5 on 2022-09-24 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameprofile',
            name='password',
            field=models.CharField(default='', max_length=300),
        ),
    ]
