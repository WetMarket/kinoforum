from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class PublishedModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Movie.Status.PUBLISHED)


class Movie(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    objects = models.Manager()
    published = PublishedModel()

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    content = models.TextField(blank=True, verbose_name="Описание")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)), default=Status.DRAFT, verbose_name="Статус")
    poster = models.ImageField(upload_to='posters/', null=True, blank=True, verbose_name="Постер")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='list', verbose_name="Категории")
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name="Жанр")
    details = models.OneToOneField('MovieDetails', on_delete=models.CASCADE, null=True, blank=True, related_name='movie', verbose_name="Детали")

    class Meta:
        ordering = ['-time_create']
        indexes = [models.Index(fields=['-time_create'])]
        verbose_name = 'кино'
        verbose_name_plural = 'Фильмы и сериалы'

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('tag', kwargs={'cat_slug': Category.slug, 'tag_slug': self.slug})

    def __str__(self):
        return self.tag


class MovieDetails(models.Model):
    release_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    rating = models.FloatField(null=True, blank=True)
    person = models.ManyToManyField('Person', blank=True, related_name='details')

    def __str__(self):
        return f"{self.movie.title} ({self.release_date.year})"


class Person(models.Model):
    name_ru = models.CharField(max_length=100, verbose_name='Имя на русском')
    name_en = models.CharField(max_length=100, verbose_name='Имя латиницей')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    photo = models.ImageField(upload_to='persons/', null=True, blank=True, verbose_name='Фото')
    bio = models.TextField(blank=True, null=True, verbose_name='Информация')
    role = models.ManyToManyField('Role', blank=True, related_name='person', verbose_name='Деятельность')

    class Meta:
        verbose_name = 'Человек'
        verbose_name_plural = 'Люди'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('person', kwargs={'person_slug': self.slug})

    def __str__(self):
        return self.name_ru


class Role(models.Model):
    role = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.role
