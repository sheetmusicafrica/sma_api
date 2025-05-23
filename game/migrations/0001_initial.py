# Generated by Django 3.1.5 on 2022-09-24 05:31

from django.db import migrations, models
import django.db.models.deletion
import sheet_music_africa.storage_backends


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('pass_phrase', models.CharField(max_length=20)),
                ('date_started', models.DateField(blank=True, null=True)),
                ('date_ended', models.DateField(blank=True, null=True)),
                ('location', models.CharField(max_length=200)),
                ('status', models.CharField(default='pending', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='GameProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=100)),
                ('pic', models.FileField(blank=True, null=True, storage=sheet_music_africa.storage_backends.GameMediaStorage(), upload_to='')),
                ('score', models.PositiveBigIntegerField(default=0)),
                ('token', models.CharField(max_length=100)),
                ('can_compete', models.BooleanField(default=False)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.competition')),
            ],
            options={
                'ordering': ['score'],
            },
        ),
    ]
