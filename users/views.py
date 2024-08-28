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
        queryset = Movie.published.all()

        rating_order = self.get_rating_order()

        # Фильтрация по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(cat=category)

        # Фильтрация по жанру
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            tag = get_object_or_404(TagPost, slug=tag_slug)
            queryset = queryset.filter(tags=tag)

        # Фильтрация по избранному
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(favorites__user=user)

        if rating_order == 'desc':
            queryset = queryset.order_by('-rating')
        elif rating_order == 'asc':
            queryset = queryset.order_by('rating')

        return queryset

    def get_rating_order(self):
        return self.request.GET.get('rating')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Избранное'
        context['rating_selected'] = self.get_rating_order()

        user = self.request.user

        # Получаем все фильмы в избранном для текущего пользователя
        favorite_movies = Movie.objects.filter(favorites__user=user).distinct()

        # Фильтрация категорий, связанных с избранными фильмами
        favorite_categories = Category.objects.filter(list__in=favorite_movies).distinct()
        context['categories'] = favorite_categories

        # Фильтрация жанров, связанных с избранными фильмами
        # Если категория выбрана, фильтруем теги по этой категории
        selected_category_slug = self.request.GET.get('category', '')

        if selected_category_slug:
            selected_category = get_object_or_404(Category, slug=selected_category_slug)
            favorite_tags = TagPost.objects.filter(id__in=Movie.objects.filter(
                cat=selected_category, id__in=favorite_movies.values('id')).values_list('tags', flat=True)).distinct()

        else:
            favorite_tags = TagPost.objects.filter(tags__in=favorite_movies).distinct()

        context['tags'] = favorite_tags

        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_tag'] = self.request.GET.get('tag', '')

        return context
