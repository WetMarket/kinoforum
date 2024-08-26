from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, ListView

from kinoforum import settings
from movies.models import Favorites, Movie, Category, TagPost
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    extra_context = {'title': "Авторизация"}


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    extra_context = {'title': "Регистрация"}
    success_url = reverse_lazy('users:login')


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'profile.html'
    extra_context = {'title': "Профиль пользователя", 'default_image': settings.DEFAULT_USER_IMAGE}

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        if 'photo' in self.request.FILES:
            self.request.user.photo = self.request.FILES['photo']
            self.request.user.save()
        return super().form_valid(form)


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "password_change_form.html"
    extra_context = {'title': "Изменение пароля"}


class FavoritesView(ListView):
    model = Movie
    template_name = 'favorites.html'
    context_object_name = 'favorites'
    paginate_by = 8

    def get_queryset(self):
        # Получаем ID избранных фильмов текущего пользователя
        favorite_ids = Favorites.objects.filter(user=self.request.user).values_list('movie_id', flat=True)
        queryset = Movie.objects.filter(id__in=favorite_ids).select_related('cat').prefetch_related('tags')

        # Фильтрация по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(cat__slug=category_slug)

        # Фильтрация по жанру
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Избранное'

        # Получаем ID избранных фильмов текущего пользователя
        favorite_ids = Favorites.objects.filter(user=self.request.user).values_list('movie_id', flat=True)
        favorite_movies = Movie.objects.filter(id__in=favorite_ids) if favorite_ids else Movie.objects.none()

        if favorite_movies.exists():
            # Получаем все категории, связанные с избранными фильмами
            categories = Category.objects.filter(id__in=favorite_movies.values_list('cat_id', flat=True)).distinct()
            context['categories'] = categories

            # Получаем жанры для фильтрации
            selected_category = self.request.GET.get('category', '')
            if selected_category:
                selected_category_obj = Category.objects.filter(slug=selected_category).first()
                if selected_category_obj:
                    tags = TagPost.objects.filter(tags__cat_id=selected_category_obj.pk).distinct()
                else:
                    tags = TagPost.objects.none()
            else:
                # Если категория не выбрана, берем все жанры из избранных фильмов
                tags = TagPost.objects.filter(tags__in=favorite_movies.values_list('tags', flat=True)).distinct()

            context['tags'] = tags
        else:
            # Если нет избранных фильмов, категории и жанры не предоставляются
            context['categories'] = []
            context['tags'] = []

        # Передаем выбранные значения в контекст
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_tag'] = self.request.GET.get('tag', '')

        return context