from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404

from movies.models import Movies, Category, TagPost, Person

menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Оставить отзыв", 'url_name': 'reviews'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Войти", 'url_name': 'login'}]


def index(request):
    posts = Movies.published.all()
    data = {
        'title': 'КИНОФОРУМ',
        'menu': menu,
        'posts': posts,
    }

    return render(request, 'movies/index.html', context=data)


def show_category(request, cat_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    posts = Movies.published.filter(cat_id=category.pk)
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
    post = get_object_or_404(Movies, slug=post_slug)
    directors = post.details.person.filter(role=1)
    data = {
        'title': post.details,
        'menu': menu,
        'post': post,
        'details': post.details,
        'cat_slug': post.cat.slug,
        'directors': directors,
    }

    return render(request, 'movies/post.html', context=data)


def show_person(request, person_slug):
    person = get_object_or_404(Person, slug=person_slug)

    data = {
        'title': person.name_ru,
        'menu': menu,
        'person': person,

    }

    return render(request, 'movies/person.html', context=data)


def show_tag_postlist(request, cat_slug, tag_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    tag = get_object_or_404(TagPost, slug=tag_slug)

    # Получаем посты, которые принадлежат данной категории и имеют указанный тег
    posts = Movies.published.filter(cat_id=category.pk, tags=tag).distinct()

    if not posts.exists():
        raise Http404

    data = {
        'title': f'{category.name}: {tag.tag}',
        'menu': menu,
        'posts': posts,
        'cat_slug': cat_slug,
    }

    return render(request, 'movies/posts_page.html', context=data)


def about(request):
    return render(request, 'movies/about.html',
                  {'title': 'О сайте', 'menu': menu})


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
