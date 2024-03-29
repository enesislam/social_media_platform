# Generated by Django 4.0.3 on 2022-03-26 06:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0023_remove_post_likes_alter_hashtag_date_added_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='post',
            name='user',
            field=models.ForeignKey(help_text='User of Post', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
