# Generated by Django 4.2.13 on 2024-08-12 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0016_alter_movie_slug_alter_movie_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Роль', 'verbose_name_plural': 'Роли'},
        ),
    ]
