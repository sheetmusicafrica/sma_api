# Generated by Django 3.1.5 on 2021-04-30 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0028_auto_20210430_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='composerprofile',
            name='country_short_code',
            field=models.CharField(blank=True, default='NG', max_length=2),
        ),
    ]