from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from movies.models import Movie, Category, TagPost, Person
from movies.forms import AddPostForm, UploadFileForm

from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.core.paginator import Paginator

from movies.utils import DataMixin

# import uuid

p = Paginator(Movie, 3)


class MovieHome(DataMixin, ListView):
    template_name = 'movies/index.html'
    context_object_name = 'post'
    title_page = 'КИНОФОРУМ'

    def get_queryset(self):
        return Movie.published.all()


class MovieCategory(DataMixin, ListView):
    template_name = 'movies/categories.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        return self.get_mixin_context(
            context,
            title=category.name,
            tags=TagPost.objects.filter(tags__cat_id=category.pk).distinct(),
            cat_slug=category.slug,
            cat_selected=category.pk,
            genre_selected=self.get_genre_slug()
        )

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs['cat_slug'])

    def get_genre_slug(self):
        return self.request.GET.get('genre')

    def get_queryset(self):
        category = self.get_category()
        genre_slug = self.get_genre_slug()

        if genre_slug:
            if not TagPost.objects.filter(slug=genre_slug).exists():
                raise Http404("Жанр не найден")
            return Movie.published.filter(cat_id=category.pk, tags__slug=genre_slug)

        return Movie.published.filter(cat_id=category.pk)


class ShowPost(DataMixin, DetailView):
    model = Movie
    template_name = 'movies/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Получаем всех режиссеров фильма
        directors = post.movie_roles.filter(role_id=1).select_related('person')
        director_people = [director.person for director in directors]

        return self.get_mixin_context(
            context,
            title=post.title,
            cat_slug=post.cat.slug,
            release_date=post.release_date,
            budget=post.budget,
            rating=post.rating,
            directors=director_people
        )

    def get_object(self, queryset=None):
        return get_object_or_404(Movie.published, slug=self.kwargs[self.slug_url_kwarg])


class ShowPerson(DataMixin, DetailView):
    model = Person
    template_name = 'movies/person.html'
    context_object_name = 'person'
    slug_url_kwarg = 'person_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object

        return self.get_mixin_context(
            context,
            title=person.name_ru,
            directed_movies=[role.movie for role in person.directed_movies]
        )

    def get_object(self, queryset=None):
        person = super().get_object(queryset)
        person.directed_movies = person.person_roles.filter(
            role_id=1,
            movie__is_published=True  # Только опубликованные фильмы
        ).select_related('movie')
        return person


class AddPage(DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'movies/addpage.html'
    title_page = 'Добавление статьи'


class UpdatePage(DataMixin, UpdateView):
    model = Movie
    form_class = AddPostForm
    template_name = 'movies/addpage.html'
    title_page = 'Редактирование статьи'


class DeletePage(DataMixin, DeleteView):
    model = Movie
    template_name = 'movies/movie_confirm_delete.html'
    context_object_name = 'movie'
    success_url = reverse_lazy('index')
    title_page = ' '


class MovieAbout(DataMixin, TemplateView):
    template_name = 'movies/about.html'
    title_page = 'О сайте'


class MovieReview(DataMixin, TemplateView):
    template_name = 'movies/reviews.html'
    title_page = 'Оставить отзыв'


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


# Из первой лабораторной
def archive(request, year):
    if year > 2024:
        return redirect('index', permanent=True)
    return HttpResponse(f"<h1>Коллекции по годам</h1><p><h2>Год: {year}</h2></p>")


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


# Лишний функционал
# def show_tag_postlist(request, cat_slug, tag_slug):
#     category = get_object_or_404(Category, slug=cat_slug)
#     tag = get_object_or_404(TagPost, slug=tag_slug)
#
#     # Получаем посты, которые принадлежат данной категории и имеют указанный тег
#     posts = Movie.published.filter(cat_id=category.pk, tags=tag).distinct()
#
#     if not posts.exists():
#         raise Http404
#
#     data = {
#         'title': f'{category.name}: {tag.tag}',
#         'menu': menu,
#         'posts': posts,
#         'cat_slug': cat_slug,
#     }
#
#     return render(request, 'movies/posts_page.html', context=data)


# def handle_uploaded_file(f):
#     name = f.name
#     ext = ''
#
#     if '.' in name:
#         ext = name[name.rindex('.'):]
#         name = name[:name.rindex('.')]
#
#     suffix = str(uuid.uuid4())
#     with open(f"uploads/{name}_{suffix}{ext}", "wb+") as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)


# def about(request):
#     if request.method == "POST":
#         form = UploadFileForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             handle_uploaded_file(form.cleaned_data['file'])
#     else:
#         form = UploadFileForm()
#
#     return render(request, 'movies/about.html',
#                   {'title': 'О сайте', 'menu': menu, 'form': form})
