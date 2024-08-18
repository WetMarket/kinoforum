from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404

from movies.models import Movie, Category, TagPost, Person, MoviePersonRole
from movies.forms import AddPostForm, UploadFileForm

import uuid


menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Оставить отзыв", 'url_name': 'reviews'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Добавление статьи", 'url_name': 'addpage'},
        {'title': "Войти", 'url_name': 'login'}]


def index(request):
    posts = Movie.published.all()
    data = {
        'title': 'КИНОФОРУМ',
        'menu': menu,
        'posts': posts,
    }

    return render(request, 'movies/index.html', context=data)


def show_category(request, cat_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    posts = Movie.published.filter(cat_id=category.pk)
    tags = TagPost.objects.filter(tags__cat_id=category.pk).distinct()

    data = {
        'title': category.name,
        'menu': menu,
        'posts': posts,
        'tags': tags,
        'cat_slug': cat_slug,
        'cat_selected': category.pk,
    }

    return render(request, 'movies/categories.html', context=data)


def show_post(request, post_slug):
    post = get_object_or_404(Movie, slug=post_slug)

    # Получаем всех режиссеров фильма
    directors = post.movie_roles.filter(role_id=1).select_related('person')
    director_people = [director.person for director in directors]

    data = {
        'title': post.title,
        'menu': menu,
        'post': post,
        'cat_slug': post.cat.slug,
        'release_date': post.release_date,
        'budget': post.budget,
        'rating': post.rating,
        'directors': director_people,
    }

    return render(request, 'movies/post.html', context=data)


def show_person(request, person_slug):
    person = get_object_or_404(Person, slug=person_slug)
    directed_movies = person.person_roles.filter(
        role_id=1,
        movie__is_published=True  # Только опубликованные фильмы
    ).select_related('movie')

    data = {
        'title': person.name_ru,
        'menu': menu,
        'person': person,
        'directed_movies': [role.movie for role in directed_movies],

    }

    return render(request, 'movies/person.html', context=data)


def show_tag_postlist(request, cat_slug, tag_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    tag = get_object_or_404(TagPost, slug=tag_slug)

    # Получаем посты, которые принадлежат данной категории и имеют указанный тег
    posts = Movie.published.filter(cat_id=category.pk, tags=tag).distinct()

    if not posts.exists():
        raise Http404

    data = {
        'title': f'{category.name}: {tag.tag}',
        'menu': menu,
        'posts': posts,
        'cat_slug': cat_slug,
    }

    return render(request, 'movies/posts_page.html', context=data)


def handle_uploaded_file(f):
    name = f.name
    ext = ''

    if '.' in name:
        ext = name[name.rindex('.'):]
        name = name[:name.rindex('.')]

    suffix = str(uuid.uuid4())
    with open(f"uploads/{name}_{suffix}{ext}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def about(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['file'])
    else:
        form = UploadFileForm()

    return render(request, 'movies/about.html',
                  {'title': 'О сайте', 'menu': menu, 'form': form})


def addpage(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.save()

            tags = form.cleaned_data['tags']
            movie.tags.set(tags)

            people_roles = form.cleaned_data['people_roles']
            for person in people_roles:
                MoviePersonRole.objects.create(movie=movie, person=person, role_id=1)

            return redirect('index')
    else:
        form = AddPostForm()

    return render(request, 'movies/addpage.html',
                  {'form': form, 'title': 'Добавить статью', 'menu': menu})


def reviews(request):
    return HttpResponse("Оставить отзыв")


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
