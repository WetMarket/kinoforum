# URL для основного приложения
from django.urls import path, register_converter

from movies import views, converters

register_converter(converters.FourDigitYearConverter, 'year4')
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('post/<int:post_id>/', views.show_post, name='post'),
    path('reviews/', views.reviews, name='reviews'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('<slug:cat_slug>/', views.show_categories, name='categories'),

    # URL первой лабораторной
    path('archive/<year4:year>/', views.archive, name='archive'),
]
