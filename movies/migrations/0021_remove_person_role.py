# Generated by Django 4.2.13 on 2024-08-13 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0020_remove_movie_people_moviepersonrole_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='role',
        ),
    ]