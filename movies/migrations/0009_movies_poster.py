# Generated by Django 4.2.13 on 2024-05-24 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0008_moviedetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='movies',
            name='poster',
            field=models.ImageField(blank=True, null=True, upload_to='posters/'),
        ),
    ]
