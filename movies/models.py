from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError

import re


def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y',
         'ъ': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class PublishedModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Movie.Status.PUBLISHED)


class Movie(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    objects = models.Manager()
    published = PublishedModel()

    # Основные поля
    title = models.CharField(max_length=255, verbose_name="Заголовок", help_text="Введите название фильма на русском")
    title_en = models.CharField(blank=True, null=True, max_length=255, verbose_name="Английское название")
    slug = models.SlugField(null=True, max_length=255, db_index=True, unique=True, blank=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name="Описание")
    poster = models.ImageField(upload_to='posters/', null=True, blank=True, verbose_name="Постер")

    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                       default=Status.DRAFT, verbose_name="Статус")

    release_date = models.DateField(blank=True, null=True, verbose_name="Дата выхода")
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Бюджет")
    rating = models.FloatField(null=True, blank=True, verbose_name="Рейтинг")

    # Связанные поля
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='list', verbose_name="Категории")
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name="Жанр")
    people_roles = models.ManyToManyField('Person', blank=True, through='MoviePersonRole', related_name='movies_roles',
                                          verbose_name="Участники")  # Участники и их роли

    class Meta:
        ordering = ['-time_create']
        indexes = [models.Index(fields=['-time_create'])]
        verbose_name = 'Кино'
        verbose_name_plural = 'Фильмы и сериалы'

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.title_en:
            self.title_en = translit_to_eng(self.title)

        if not self.slug:
            base_slug = slugify(self.title_en)

            # Проверяем, есть ли дата выхода
            if self.release_date:
                slug_with_year = f"{base_slug}-{self.release_date.year}"
            else:
                slug_with_year = base_slug

            unique_slug = slug_with_year
            num = 1
            while Movie.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{slug_with_year}-{num}"
                num += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)

    def clean(self):
        if self.budget and self.budget < 0:
            raise ValidationError('Бюджет не может быть отрицательным.')

        if self.title and not re.match(r'^[а-яА-ЯёЁ0-9\s\-\'\":,]+$', self.title):
            raise ValidationError("Название должно содержать только русские буквы и допустимые символы.")

        if self.title_en and not re.match(r'^[a-zA-Z0-9\s\-\'\":,]+$', self.title_en):
            raise ValidationError("Название должно содержать только английские буквы и допустимые символы.")

    def __str__(self):
        return self.title


# Категории (фильмы/сериалы/ и тд)
class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name


# Жанры
class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True, verbose_name='Жанр')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def get_absolute_url(self):
        return reverse('tag', kwargs={'cat_slug': Category.slug, 'tag_slug': self.slug})

    def __str__(self):
        return self.tag


# Люди
class Person(models.Model):
    name_ru = models.CharField(max_length=100, verbose_name='Имя на русском')
    name_en = models.CharField(max_length=100, verbose_name='Имя латиницей')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    photo = models.ImageField(upload_to='persons/', null=True, blank=True, verbose_name='Фото')
    bio = models.TextField(blank=True, null=True, verbose_name='Информация')
    m_count = models.IntegerField(blank=True, default=0)

    class Meta:
        verbose_name = 'Участник фильма'
        verbose_name_plural = 'Участники фильмов'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('person', kwargs={'person_slug': self.slug})

    def __str__(self):
        return self.name_ru


class Role(models.Model):
    role = models.CharField(max_length=100, db_index=True, verbose_name="Роль")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def delete(self, *args, **kwargs):
        # Проверяем, есть ли связанные записи в MoviePersonRole
        if MoviePersonRole.objects.filter(role=self).exists():
            raise ValidationError("Невозможно удалить роль, так как она используется в связях с фильмами.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.role


class MoviePersonRole(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_roles')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_movie')

    class Meta:
        verbose_name = 'Участник фильма и его роль'
        verbose_name_plural = 'Участники фильмов и их роли'
        unique_together = ('movie', 'person', 'role')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.person.name_ru} - {self.role.role} в {self.movie.title}"
