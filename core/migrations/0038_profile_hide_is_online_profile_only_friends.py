# Generated by Django 4.0.3 on 2022-04-01 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_alter_notificaton_notification_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='hide_is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='only_friends',
            field=models.BooleanField(default=False),
        ),
    ]
