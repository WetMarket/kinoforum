# Generated by Django 4.2.13 on 2024-08-12 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0012_alter_category_options_alter_movie_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movie',
            options={'ordering': ['-time_create'], 'verbose_name': 'Кино', 'verbose_name_plural': 'Фильмы и сериалы'},
        ),
        migrations.AlterModelOptions(
            name='tagpost',
            options={'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
        migrations.RemoveField(
            model_name='movie',
            name='details',
        ),
        migrations.AddField(
            model_name='movie',
            name='budget',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Бюджет'),
        ),
        migrations.AddField(
            model_name='movie',
            name='people',
            field=models.ManyToManyField(blank=True, related_name='movies', to='movies.person', verbose_name='Участники'),
        ),
        migrations.AddField(
            model_name='movie',
            name='rating',
            field=models.FloatField(blank=True, null=True, verbose_name='Рейтинг'),
        ),
        migrations.AddField(
            model_name='movie',
            name='release_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата выхода'),
        ),
        migrations.AlterField(
            model_name='tagpost',
            name='tag',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Жанр'),
        ),
        migrations.DeleteModel(
            name='MovieDetails',
        ),
    ]