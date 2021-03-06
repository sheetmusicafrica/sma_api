# Generated by Django 3.1.5 on 2021-03-22 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('composer', '0013_auto_20210319_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='composerprofile',
            name='background_image',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='composerprofile',
            name='discription',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.CreateModel(
            name='ComposerAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=50)),
                ('bank_code', models.CharField(max_length=10)),
                ('account_number', models.CharField(max_length=50)),
                ('composer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='composer.composerprofile')),
            ],
        ),
    ]
