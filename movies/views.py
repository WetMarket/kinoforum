from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponseNotFound, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView

from movies.models import Movie, Category, TagPost, Person, Favorites, MovieReaction
from movies.forms import AddPostForm, CommentForm
from movies.utils import DataMixin

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

p = Paginator(Movie, 3)


@login_required
def add_favorites(request, post_slug):
    movie = get_object_or_404(Movie, slug=post_slug)
    Favorites.objects.get_or_create(user=request.user, movie=movie)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_favorites(request, post_slug):
    movie = get_object_or_404(Movie, slug=post_slug)
    Favorites.objects.filter(user=request.user, movie=movie).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def toggle_reaction(request, post_slug, reaction_type):
    movie = get_object_or_404(Movie, slug=post_slug)

    # Попробуем найти существующую реакцию
    reaction = MovieReaction.objects.filter(user=request.user, movie=movie).first()

    if reaction:
        if reaction_type == 'like':
            if reaction.is_like is True:
                reaction.delete()
            else:
                reaction.is_like = True
                reaction.save()
        elif reaction_type == 'dislike':
            if reaction.is_like is False:
                reaction.delete()
            else:
                reaction.is_like = False
                reaction.save()
    else:
        if reaction_type == 'like':
            MovieReaction.objects.create(user=request.user, movie=movie, is_like=True)
        elif reaction_type == 'dislike':
            MovieReaction.objects.create(user=request.user, movie=movie, is_like=False)

    return redirect(request.META.get('HTTP_REFERER', '/'))


class MovieHome(DataMixin, ListView):
    template_name = 'movies/index.html'
    context_object_name = 'post'
    title_page = 'КИНОФОРУМ'

    def get_queryset(self):
        queryset = Movie.published.all()

        # Проверка параметра сортировки
        rating = self.request.GET.get('rating')
        if rating == 'desc':
            queryset = queryset.order_by('-rating')
        elif rating == 'asc':
            queryset = queryset.order_by('rating')

        return queryset


class MovieCategory(DataMixin, ListView):
    template_name = 'movies/categories.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()

        context.update({
            'title': category.name,
            'tags': TagPost.objects.filter(tags__cat_id=category.pk).distinct(),
            'cat_slug': category.slug,
            'cat_selected': category.pk,
            'genre_selected': self.get_genre_slug(),
            'rating_selected': self.get_rating_order(),
        })

        return context

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs['cat_slug'])

    def get_genre_slug(self):
        return self.request.GET.get('genre')

    def get_rating_order(self):
        return self.request.GET.get('rating')

    def get_queryset(self):
        category = self.get_category()
        genre_slug = self.get_genre_slug()
        rating_order = self.get_rating_order()

        queryset = Movie.published.filter(cat_id=category.pk)

        if genre_slug:
            if not TagPost.objects.filter(slug=genre_slug).exists():
                raise Http404("Жанр не найден")
            queryset = queryset.filter(tags__slug=genre_slug)

        if rating_order == 'desc':
            queryset = queryset.order_by('-rating')
        elif rating_order == 'asc':
            queryset = queryset.order_by('rating')

        return queryset


class ShowPost(DataMixin, DetailView):
    model = Movie
    template_name = 'movies/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Получаем всех режиссеров фильма
        directors = post.movie_roles.filter(role_id=1).select_related('person')
        director_people = [director.person for director in directors]

        comments = post.comments.all()
        paginator = Paginator(comments, self.paginate_by)
        page = self.request.GET.get('page')

        is_favorite = Favorites.objects.filter(user=self.request.user, movie=post).exists() \
            if self.request.user.is_authenticated else False

        favorites_count = Favorites.objects.filter(movie=post).count()

        like_count = MovieReaction.objects.filter(movie=post, is_like=True).count()
        dislike_count = MovieReaction.objects.filter(movie=post, is_like=False).count()

        user_reaction = None
        if self.request.user.is_authenticated:
            try:
                user_reaction = MovieReaction.objects.get(user=self.request.user, movie=post)
            except MovieReaction.DoesNotExist:
                user_reaction = None

        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        context.update({
            'comments': comments,
            'form': CommentForm(),
            'is_favorite': is_favorite,
            'favorites_count': favorites_count,
            'user_reaction': user_reaction,
            'like_count': like_count,
            'dislike_count': dislike_count,
        })

        return self.get_mixin_context(
            context,
            title=post.title,
            cat_slug=post.cat.slug,
            release_date=post.release_date,
            budget=post.budget,
            rating=post.rating,
            directors=director_people
        )

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = self.get_object()
            comment.author = self.request.user
            comment.save()
            return redirect(self.request.path)
        return self.render_to_response(self.get_context_data(form=form))

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


class AddPage(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'movies/addpage.html'
    title_page = 'Добавление статьи'
    permission_required = 'movies.add_movie'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class UpdatePage(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, UpdateView):
    model = Movie
    form_class = AddPostForm
    template_name = 'movies/addpage.html'
    title_page = 'Редактирование статьи'
    permission_required = 'movies.change_movie'


class DeletePage(LoginRequiredMixin, DataMixin, DeleteView):
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


class MovieContact(DataMixin, TemplateView):
    template_name = 'movies/contact.html'
    title_page = 'Обратная связь'


# Из первой лабораторной
@login_required
@permission_required(perm='movies.view_movie', raise_exception=True)
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
