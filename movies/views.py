from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404

from movies.models import Movies

menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Оставить отзыв", 'url_name': 'reviews'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Войти", 'url_name': 'login'}]

# Добавил категории для сайта
categories_db = [{'title': "ФИЛЬМЫ", 'url_name': 'movies'},
                 {'title': "СЕРИАЛЫ", 'url_name': 'series'},
                 {'title': "МУЛЬТФИЛЬМЫ", 'url_name': 'animation'}, ]


def index(request):
    posts = Movies.published.all()
    data = {
        'title': 'КИНОФОРУМ',
        'menu': menu,
        'posts': posts,
    }
    return render(request, 'movies/index.html', context=data)



def about(request):
    return render(request, 'movies/about.html',
                  {'title': 'О сайте', 'menu': menu})


def show_post(request, post_slug):
    post = get_object_or_404(Movies, slug=post_slug)
    data = {
        'title': post.title,
        'menu': menu,
        'post': post,
        'cat_selected': 1,
    }
    return render(request, 'movies/post.html', context=data)


def reviews(request):
    return HttpResponse("Оставить отзыв")


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


def show_categories(request, cat_slug):
    for category in categories_db:
        if category['url_name'] == cat_slug:
            return HttpResponse(f"Категория {category['title']}")


# Из первой лабораторной
def archive(request, year):
    if year > 2024:
        return redirect('index', permanent=True)
    return HttpResponse(f"<h1>Коллекции по годам</h1><p><h2>Год: {year}</h2></p>")


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
