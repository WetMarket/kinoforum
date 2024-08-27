# URL для основного приложения
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, register_converter
from movies import views, converters

register_converter(converters.FourDigitYearConverter, 'year4')

urlpatterns = [
    # Главная и основные страницы
    path('', views.MovieHome.as_view(), name='index'),
    path('about/', views.MovieAbout.as_view(), name='about'),
    path('contact/', views.MovieContact.as_view(), name='contact'),
    path('reviews/', views.MovieReview.as_view(), name='reviews'),

    # CRUD-операции
    path('addpage/', views.AddPage.as_view(), name='addpage'),
    path('edit/<int:pk>/', views.UpdatePage.as_view(), name='edit_page'),
    path('watch/<slug:slug>/delete/', views.DeletePage.as_view(), name='movie_delete'),

    # Детализированные страницы
    path('watch/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('person/<slug:person_slug>/', views.ShowPerson.as_view(), name='person'),

    # Действия над объектами
    path('watch/<slug:post_slug>/favorites/add/', views.add_favorites, name='add_favorites'),
    path('watch/<slug:post_slug>/favorites/remove/', views.remove_favorites, name='remove_favorites'),
    path('watch/<slug:post_slug>/<str:reaction_type>/', views.toggle_reaction, name='toggle_reaction'),

    # Фильтрация и категории
    path('<slug:cat_slug>/', views.MovieCategory.as_view(), name='category'),

    # Из первой лаб. работы
    path('archive/<year4:year>/', views.archive, name='archive'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
