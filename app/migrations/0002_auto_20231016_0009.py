# Generated by Django 3.2.10 on 2023-10-16 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='synctask',
            name='synced_file',
        ),
        migrations.AddField(
            model_name='synctask',
            name='synced_file_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]