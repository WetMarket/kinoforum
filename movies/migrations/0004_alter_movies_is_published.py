# Generated by Django 4.2.13 on 2024-05-13 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_alter_movies_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movies',
            name='is_published',
            field=models.BooleanField(choices=[(0, 'Черновик'), (1, 'Опубликовано')], default=0),
        ),
    ]