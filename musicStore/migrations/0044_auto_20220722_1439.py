# Generated by Django 3.1.5 on 2022-07-22 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicStore', '0043_sheetmusic_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sheetmusic',
            options={'ordering': ['-pk']},
        ),
        migrations.AddField(
            model_name='sheetmusic',
            name='composed_by',
            field=models.TextField(default=''),
        ),
    ]