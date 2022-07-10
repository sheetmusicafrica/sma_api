# Generated by Django 3.1.5 on 2021-03-04 13:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('musicStore', '0022_remove_sheetmusic_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sheetmusic',
            name='composer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
