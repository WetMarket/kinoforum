from django.contrib import admin, messages
from .models import Movie, Category, Person, TagPost


class GenreFilter(admin.SimpleListFilter):
    title = 'Жанр'
    parameter_name = 'genre'

    def lookups(self, request, model_admin):
        genres = TagPost.objects.all()
        return [(genre.id, genre.tag) for genre in genres]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__id__exact=self.value())
        return queryset


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_create', 'is_published', 'cat', 'brief_info', 'director_info')
    list_display_links = ('title',)
    ordering = ['time_create', 'title']
    list_editable = ('is_published', 'cat')
    list_per_page = 10
    actions = ['set_published', 'set_draft']
    search_fields = ['title', 'cat__name']
    list_filter = ['cat__name', 'is_published', GenreFilter]


    @admin.display(description="Краткое описание")
    def brief_info(self, movie: Movie):
        return f"Описание {len(movie.content)} символов."

    @admin.display(description="Режиссер")
    def director_info(self, movie: Movie):
        return ", ".join([person.name_ru for person in movie.details.person.all()])

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        queryset.update(is_published=Movie.Status.PUBLISHED)

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Movie.Status.DRAFT)
        self.message_user(request, f"{count} записи(ей) сняты с публикации!", messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    ordering = ['-name']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name_ru',)
    list_display_links = ('name_ru',)
    ordering = ['name_ru']
