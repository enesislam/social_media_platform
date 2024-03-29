# Generated by Django 4.0.3 on 2022-03-22 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='mail',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.png', upload_to='user_profiles'),
        ),
    ]
