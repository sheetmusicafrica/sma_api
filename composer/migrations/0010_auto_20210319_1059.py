# Generated by Django 3.1.5 on 2021-03-19 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0009_userpaymenthistory_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='composerprofile',
            name='facebook_link',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='composerprofile',
            name='soundcloud_link',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='composerprofile',
            name='twitter_link',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='composerprofile',
            name='youtube_link',
            field=models.TextField(blank=True, default=''),
        ),
    ]
