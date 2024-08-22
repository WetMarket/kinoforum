# URL для основного приложения
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, register_converter
from movies import views, converters

register_converter(converters.FourDigitYearConverter, 'year4')

urlpatterns = [
    path('', views.MovieHome.as_view(), name='index'),
    path('about/', views.MovieAbout.as_view(), name='about'),
    path('addpage/', views.AddPage.as_view(), name='addpage'),
    path('reviews/', views.MovieReview.as_view(), name='reviews'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),

    path('watch/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('person/<slug:person_slug>/', views.ShowPerson.as_view(), name='person'),

    path('edit/<int:pk>/', views.UpdatePage.as_view(), name='edit_page'),
    path('watch/<slug:slug>/delete/', views.DeletePage.as_view(), name='movie_delete'),

    path('<slug:cat_slug>/', views.MovieCategory.as_view(), name='category'),


    # path('<slug:cat_slug>/<slug:tag_slug>/', views.show_tag_postlist, name='tag'),


    # URL первой лабораторной
    path('archive/<year4:year>/', views.archive, name='archive'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
