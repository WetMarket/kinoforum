# URL для основного приложения
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, register_converter
from movies import views, converters

register_converter(converters.FourDigitYearConverter, 'year4')

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('addpage/', views.addpage, name='addpage'),
    path('watch/<slug:post_slug>/', views.show_post, name='post'),
    path('person/<slug:person_slug>/', views.show_person, name='person'),
    path('reviews/', views.reviews, name='reviews'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('<slug:cat_slug>/', views.show_category, name='category'),
    path('<slug:cat_slug>/<slug:tag_slug>/', views.show_tag_postlist, name='tag'),


    # URL первой лабораторной
    path('archive/<year4:year>/', views.archive, name='archive'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

