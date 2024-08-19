from django.contrib import admin, messages
from .models import Movie, Category, Person, TagPost, Role, MoviePersonRole
from django.utils.safestring import mark_safe


# Инлайн для заполнения состава фильма
class MoviePersonRoleInline(admin.TabularInline):
    model = MoviePersonRole
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person":
            kwargs["queryset"] = Person.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CategoryReverseFilter(admin.SimpleListFilter):
    title = 'Категория'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        # Категории, отсортированные в обратном порядке
        categories = Category.objects.all().order_by('-name')
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cat__id__exact=self.value())
        return queryset


class GenreFilter(admin.SimpleListFilter):
    title = 'Жанр'
    parameter_name = 'genre'

    def lookups(self, request, model_admin):
        genres = TagPost.objects.all().order_by('tag')
        return [(genre.id, genre.tag) for genre in genres]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__id__exact=self.value())
        return queryset


class RoleFilter(admin.SimpleListFilter):
    title = 'Роль'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        roles = Role.objects.all().order_by('role')
        return [(role.id, role.role) for role in roles]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person_roles__role__id=self.value())
        return queryset


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'post_poster',
        'title',
        'category_display',
        'genres_display',
        'release_date_year',
        'rating',
        'director_info',
        'is_published',
        # 'brief_info',
    )

    fields = ('title', 'title_en', 'slug', 'cat', 'release_date', 'rating', 'budget',
              'poster', 'post_poster', 'tags', 'content', 'is_published', 'time_create', 'time_update')

    list_display_links = ('title', )
    list_editable = ('is_published',)
    list_per_page = 15
    list_filter = [CategoryReverseFilter, GenreFilter, 'is_published']

    search_fields = ['title', 'title_en', 'cat__name', 'tags__tag',
                     'people_roles__name_ru', 'people_roles__name_en']
    readonly_fields = ['post_poster', 'time_create', 'time_update']
    # ordering = ['people_roles__name_ru', 'title']
    ordering = ['title']
    actions = ['set_published', 'set_draft']
    inlines = [MoviePersonRoleInline]

    save_on_top = True

    @admin.display(description="Изображение")
    def post_poster(self, movie: Movie):
        if movie.poster:
            return mark_safe(f"<img src='{movie.poster.url}' width=50>")
        return "Без постера"

    @admin.display(description="Категория")
    def category_display(self, movie: Movie):
        return movie.cat.name

    @admin.display(description="Жанры")
    def genres_display(self, movie: Movie):
        return ", ".join(tag.tag for tag in movie.tags.all())

    @admin.display(description="Год", ordering="release_date")
    def release_date_year(self, movie: Movie):
        return movie.release_date.year if movie.release_date else "Не указан"

    @admin.display(description="Описание")
    def brief_info(self, movie: Movie):
        return f"Описание {len(movie.content)} символов."

    @admin.display(description="Режиссер", ordering="people_roles__name_ru")
    def director_info(self, movie: Movie):
        # Фильтруем MoviePersonRole по текущему фильму и роли
        directors = movie.movie_roles.filter(role_id=1)
        return ", ".join([mpr.person.name_ru for mpr in directors])

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Movie.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записи(ей).")

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
    list_display = ('name_ru', 'name_en', 'role_display')
    list_display_links = ('name_ru',)
    ordering = ['name_ru']
    search_fields = ['name_ru', 'name_en']
    list_filter = [RoleFilter]

    fields = ('name_ru', 'name_en', 'slug', 'photo', 'post_photo', 'bio', 'movie_roles_info')
    readonly_fields = ('post_photo', 'movie_roles_info',)
    exclude = ('m_count', 'role')

    def movie_roles_info(self, person: Person):
        roles = MoviePersonRole.objects.filter(person=person)
        if not roles.exists():
            return "Нигде не участвовал"
        return "\n".join([f"{role.role.role} в {role.movie.title} "
                          f"({role.movie.release_date.year})" for role in roles])

    movie_roles_info.short_description = "Деятельность"

    @admin.display(description="Изображение")
    def post_photo(self, person: Person):
        if person.photo:
            return mark_safe(f"<img src='{person.photo.url}' width=50>")
        return "Без постера"

    @admin.display(description="Деятельность")
    def role_display(self, person: Person):
        # Все роли, связанные с человеком через модель MoviePersonRole
        roles = person.person_roles.values_list('role__role', flat=True).distinct()
        return ", ".join(roles)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role',)
    search_fields = ['role']

    def delete_model(self, request, obj):
        if MoviePersonRole.objects.filter(role=obj).exists():
            self.message_user(request, "Невозможно удалить роль, так как она используется в фильмах.",
                              messages.ERROR)
            return
        super().delete_model(request, obj)


@admin.register(TagPost)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    search_fields = ['tag']
    ordering = ['tag']
