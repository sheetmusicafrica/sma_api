# Generated by Django 3.1.5 on 2021-03-25 21:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('musicStore', '0027_auto_20210324_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='my_review',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
