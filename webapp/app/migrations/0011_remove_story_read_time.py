# Generated by Django 5.0 on 2024-04-21 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_story_read_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='read_time',
        ),
    ]