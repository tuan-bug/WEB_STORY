# Generated by Django 5.0 on 2024-05-02 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_chat_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='description',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
